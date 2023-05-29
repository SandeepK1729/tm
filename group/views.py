from django.shortcuts               import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.core                    import serializers

from .models                        import Group, Transaction
from .decorators                    import group_member_login_required

from core.models                    import User 
from datetime                       import date
from time                           import sleep

@login_required
def groups_view(request):
    context = {
        'title' : "Groups",
    }
    if request.method == "POST":
        try:
            group = Group(name = request.POST.get("group_name"), created_by = request.user)
            group.save()
            context['message'] = f"Group named {group.name} created successfully"
        except Exception as e:
            context['message'] = f"Group not created, because of {e}"      

    return render(request, "pages/groups.html", context)

@login_required
@group_member_login_required
def group_view(request, group):
    context = {
        'group' : group,
        'not_exist' : [],
        'already_exist' : [],
        'added' : [],
        'title' : group.name,
    }

    if request.method == "POST":
        usernames = [username.strip() for username in request.POST.get("username", '').split(',')]

        for username in usernames:
            user = None
            try:
                user = User.objects.get(username = username)
            except Exception as e:
                if user is None:
                    context['not_exist'].append(username)
                
            else:
                if user in group.get_members:
                    context['already_exist'].append(username)
                else:
                    group.add_member(user)
                    context['added'].append(username)
                    

        contexts = [
            f"{', '.join(context['not_exist'])} {'is' if len(context['not_exist']) == 1 else 'are'} not exist"                  if len(context['not_exist']) != 0       else "",
            f"{', '.join(context['already_exist'])} {'is' if len(context['already_exist']) == 1 else 'are'} already in group"   if len(context['already_exist']) != 0   else "",
            f"{', '.join(context['added'])} {'is' if len(context['added']) == 1 else 'are'} added to group"                     if len(context['added']) != 0           else "",
        ]
        context['message'] = ", ".join(filter(lambda x : x != "", contexts))

    return render(request, "pages/group.html", context)

@login_required
@group_member_login_required
def remove_group_member(request, group, username):
    try:
        user = User.objects.get(username = username)

        if user == request.user or request.user == group.created_by:
            user.groups.remove(group)
    except Exception as e:
        pass
    
    return redirect(f'/group/{group.id}')

@login_required
@group_member_login_required
def group_transactions_view(request, group):
    return render(request, 'pages/transactions.html', {
        'group' : group,
        'title' : f'{group.name} Group Transactions'    
    })

@login_required
@group_member_login_required
def add_group_transaction_view(request, group):
    return render(request, 'pages/add_transaction.html', {
        'group' : group,
        'title' : f'Add Transaction in {group.name} Group'
    })

def api_group_transactions_view(request, id):
    group = Group.objects.get(id = id)

    if request.method == "POST":

        transaction = Transaction(
            transaction_for = request.POST.get("for"),
            by              = User.objects.get(username = request.POST.get("by")),
            to              = request.POST.get("to"),
            of_group        = group,
            amount          = request.POST.get("amount"),
        )
        transaction.save()

        return redirect(f"/group/{group.id}/transactions")

    try:

        # fetch transactions and return
        transactions = Transaction.objects.filter(of_group = group)

        # date based filtering on transactions
        # start point
        start_point = request.GET.get('start_date', '*')

        if start_point != "*":
            start_point = date(*[int(x) for x in start_point.split('-')])
            transactions = transactions.filter(on__gte=start_point)
        
        # stop point
        stop_point  = request.GET.get('stop_date', '*')

        if stop_point != "*":
            stop_point = date(*[int(x) for x in stop_point.split('-')])
            transactions = transactions.filter(on__lte=stop_point)
        

        # user filter
        username = request.GET.get('username', '*')

        if username != "*":
            user = User.objects.get(username = username)
            transactions = transactions.filter(by = user)
        
        # trasaction ordering on descending time
        transactions = transactions.order_by('-id')

        json = serializers.serialize("json", transactions, use_natural_foreign_keys=True)
        return HttpResponse(json) 

    except Exception as e:
        print(e, end = "\n" * 3)
        return HttpResponse("")

@login_required
@group_member_login_required
def group_transactions_monthly_split(request, group):

    # fetch transactions and return
    transactions = Transaction.objects.filter(of_group = group)

    # date based filtering on transactions
    # start point
    start_point = request.GET.get('start_point', date.today().strftime("%Y-%m-%d")[:-2] + "01")
    start_date  = start_point
    
    if start_point != "*":
        start_point = date(*[int(x) for x in start_point.split('-')])
        transactions = transactions.filter(on__gte=start_point)
    
    # stop point    
    stop_point  = request.GET.get('stop_point', date.today().strftime("%Y-%m-%d"))
    stop_date   = stop_point

    if stop_point != "*":
        stop_point = date(*[int(x) for x in stop_point.split('-')])
        transactions = transactions.filter(on__lte=stop_point)
        
    members = { member.username : 0 for member in group.get_members }
    total_amount = 0
    for transaction in transactions:
        members[transaction.by.username] += transaction.amount
        total_amount += transaction.amount

    each_person_contribution = round(total_amount / len(members))

    rows = []
    for member, spend in members.items():
        rows.append([
            member, 
            spend, 
            0 if each_person_contribution >  spend else spend - each_person_contribution,
            0 if each_person_contribution <= spend else each_person_contribution - spend,
        ])
    
    
    return render(request, 'pages/transactions_split.html', {
        'rows' : rows,
        'split': each_person_contribution,
        'total': total_amount,
        'start_point' : start_date,
        'stop_point' : stop_date,
        'group' : group,
        'title' : f'{group.name} Group Transactions Split'
    })

    