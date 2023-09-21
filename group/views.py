from django.shortcuts               import render, HttpResponse, redirect, reverse
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
        'groups' : request.user.groups.all().select_related('created_by').order_by('-id'),
    }
    
    if request.method == "POST":
        try:
            group = Group.objects.create(name = request.POST.get("group_name"), created_by = request.user)
            group.save()
            context['message'] = f"Group named {group.name} created successfully"
        except Exception as e:
            context['message'] = f"Group not created, because of {e}" 
            print("error :", context['message'])     

    context['groups'] = request.user.groups.all().select_related('created_by').order_by('-id')
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
        'title' : f'Add Transaction in {group.name} Group',
        'is_individual_group' : len(group.get_members) == 1,
        'transaction' : None,
    })
    
@login_required
@group_member_login_required
def info_group_transaction_view(request, group):
    if "id" not in request.GET:
        return redirect(to = f'/group/{group.id}/transactions')
        
    return render(request, 'pages/add_transaction.html', {
        'group' : group,
        'title' : f'Transaction Info of {group.name} Group',
        'is_individual_group' : len(group.get_members) == 1,
        'transaction' : Transaction.objects.get(id = request.GET.get('id')),
        'savings' : User.objects.get(username = "savings"),
        'transaction' : Transaction.objects.filter(id = request.GET.get('id')).first() if "id" in request.GET else None,
    })

def api_group_transactions_view(request, id):
    group = Group.objects.get(id = id)

    if request.method == "POST":
        request_POST = {x : y for x, y in request.POST.lists()}
        request.POST = request.POST.dict()
        
        transaction_id = int(request.POST.get("transaction_id"))
        transaction = None
        
        if transaction_id == 0:
            transaction = Transaction()
        else:
            transaction = Transaction.objects.get(id = transaction_id)
            if transaction.added_by != request.user:
                return HttpResponse("You are not allowed to edit this transaction")

        if request.POST.get("action") == "delete":
            transaction.delete()
            return redirect(to = f'/group/{group.id}/transactions')
        
        savings_account_balance     = group.savings

        old_transaction_amount = transaction.amount if transaction.id is not None else 0

    
        transaction.transaction_for = request.POST.get("for")
        transaction.by              = User.objects.get(username = request.POST.get("by"))
        transaction.to              = request.POST.get("to")
        transaction.of_group        = group
        transaction.amount          = int(request.POST.get("amount"))
        transaction.on              = request.POST.get("on")
        transaction.added_by        = request.user

        
        if request.POST.get("is_it_for_savings", "off") == "on":
            transaction.transaction_for = "savings"
            transaction.to = "savings"

        transaction.save()
        
        transaction.share_to.clear()

        if "share_to" in request_POST:
            share_to = [User.objects.get(username = username) for username in request_POST.get("share_to", [])]
        else:
            share_to = group.get_members

        transaction.share_to.add(*share_to)

        print("adding to savings")
        change_amount = transaction.amount - old_transaction_amount
        print("change_amount ", change_amount)

        print(transaction, transaction.transaction_for, transaction.by)
        if transaction.transaction_for == "savings":
            savings_account_balance += change_amount
            print("savings_account_balance after adding ", savings_account_balance)
        if transaction.by.username == "savings":
            savings_account_balance -= change_amount
            print("savings_account_balance after using ", savings_account_balance)

        group.savings = savings_account_balance
        group.save()

        return redirect(to = f'/group/{group.id}/transactions')

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
        

        # # user filter
        # username = request.GET.get('username', '*')

        # if username != "*":
        #     user = User.objects.get(username = username)
        #     transactions = transactions.filter(by = user)

        # # share to filter
        # share_to = request.GET.get('share_to', '*')

        # if share_to != "*":
        #     user = User.objects.get(username = share_to)
        #     transactions = transactions.filter(share_to = user)
        
        # trasaction ordering on descending time
        transactions = transactions.order_by('-on')

        json = serializers.serialize("json", transactions, use_natural_foreign_keys=True)
        return HttpResponse(json) 

    except Exception as e:
        print(e, end = "\n" * 3)
        return HttpResponse("")

@login_required
@group_member_login_required
def group_transactions_monthly_split(request, group):

    # fetch transactions and return
    transactions = group.transactions.all()

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
    
    members = { 
        member.username : {
            'given' : 0,
            'share' : 0,
        } for member in group.get_members
    }
    
    total_amount = 0            # total amount given by all the members
    total_spend_amount = 0      # total amount spend by group
    
    for transaction in transactions:
        
        # if transaction for is savings then add to total amount not to total spend amount
        if transaction.transaction_for == "savings":
            members[transaction.by.username]['given'] += transaction.amount # add to user given amount
            total_amount += transaction.amount                              # add to total amount

            continue
        
        # if transaction by is member then add to individual given amount
        if transaction.by.username != "savings":
            members[transaction.by.username]['given'] += transaction.amount # add to user given amount
    
        # wheather transaction by is savings or by user then add to total spend amount not to total amount
        total_spend_amount += transaction.amount    # add to total spend amount
        total_amount += transaction.amount          # add to total amount 
        
        # split the amount to all the shared members
        for user in transaction.share_to.all():     # for each shared member
            members[user.username]['share'] += transaction.amount / len(transaction.share_to.all()) # add to shared amount


    rows = []
    for member, money in members.items():
        money['share'] = int(money['share'])

        rows.append([
            member, 
            money['given'],
            money['share'], 
            0 if money['share'] >  money['given'] else money['given'] - money['share'],
            0 if money['share'] <  money['given'] else money['share'] - money['given'],
        ])
    
    
    return render(request, 'pages/transactions_split.html', {
        'rows' : rows,
        'total_amount': total_amount,
        'total_spend_amount' : total_spend_amount,
        'total_savings' : total_amount - total_spend_amount,
        'start_point' : start_date,
        'stop_point' : stop_date,
        'group' : group,
        'title' : f'{group.name} Group Transactions Split'
    })

    