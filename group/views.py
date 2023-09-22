from django.shortcuts               import render, HttpResponse, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.core                    import serializers

from .models                        import Group, Transaction
from .decorators                    import group_member_login_required

from core.models                    import User 
from datetime                       import date

from .helper                        import round_up, custom_render

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

    context['groups'] = request.user.groups.all().select_related('created_by').order_by('-id')
    return custom_render(request, "pages/groups.html", context)

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
            except User.DoesNotExist:
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

    return custom_render(request, "pages/group.html", context)

@login_required
@group_member_login_required
def group_settings_view(request, group):
    return render(request, "pages/group_settings.html", {
        'group' : group,
        'title' : f"{group.name} Group Settings",
    })

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
    return custom_render(request, 'pages/transactions.html', {
        'group' : group,
        'title' : f'{group.name} Group Transactions',
        'savings' : User.objects.get(username = "savings")
    })

@login_required
@group_member_login_required
def add_group_transaction_view(request, group):
    return custom_render(request, 'pages/add_transaction.html', {
        'group' : group,
        'title' : f'Add Transaction in {group.name} Group',
        'is_individual_group' : len(group.get_members) == 1,
        'savings' : User.objects.get(username = "savings"),
        'transaction' : Transaction.objects.get(id = request.GET.get("id")) if request.GET.get("id") else None,
    })
    
@login_required
@group_member_login_required
def api_group_transactions_view(request, group):
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

        change_amount = transaction.amount - old_transaction_amount

        if transaction.transaction_for == "savings":
            savings_account_balance += change_amount
        if transaction.by.username == "savings":
            savings_account_balance -= change_amount

        group.savings = savings_account_balance
        group.save()

        return redirect(to = f'/group/{group.id}/transactions')

    try:
        # date based filtering on transactions
        # start point
        start_point = request.GET.get('start_date', '*')

        if start_point != "*":
            start_point = date(*[int(x) for x in start_point.split('-')])
        
        # stop point
        stop_point  = request.GET.get('stop_date', '*')

        if stop_point != "*":
            stop_point = date(*[int(x) for x in stop_point.split('-')])
        
        transactions = group.transactions.filter(
                on__range=[start_point, stop_point]
            ).select_related(
                'by', 'added_by'
            ).prefetch_related(
                'share_to'
            ).order_by(
                '-on', '-id'
            )

        json = serializers.serialize(
            "json", 
            transactions,
            use_natural_foreign_keys = True
        )
        return HttpResponse(json) 

    except Exception as e:
        return HttpResponse("")

@login_required
@group_member_login_required
def group_transactions_monthly_split(request, group):
    # # date based filtering on transactions
    # start point
    start_point = request.GET.get('start_point', date.today().strftime("%Y-%m-%d")[:-2] + "01")
    start_date  = start_point
    
    if start_point != "*":
        start_point = date(*[int(x) for x in start_point.split('-')])
    
    # stop point    
    stop_point  = request.GET.get('stop_point', date.today().strftime("%Y-%m-%d"))
    stop_date   = stop_point

    if stop_point != "*":
        stop_point = date(*[int(x) for x in stop_point.split('-')])
    
    members = { 
        member.username : {
            'given' : 0,
            'share' : 0,
        } for member in group.get_members
    }
    
    total_saved_amount = 0              # total amount given by all the members
    total_spend_amount = 0              # total amount spend by group
    
    transactions = group.transactions.filter(  
            of_group=group,                                 # filter by group
            on__gte=start_point,                            # filter by start point 
            on__lte=stop_point,                             # filter by stop point
        ).select_related('by').prefetch_related('share_to')
    
    for transaction in transactions:
        
        # if transaction for is savings then add to total amount not to total spend amount
        if transaction.transaction_for == "savings":
            members[transaction.by.username]['given'] += transaction.amount # add to user given amount
            total_saved_amount += transaction.amount                         # add to total amount

        else:
            # if transaction by is member then add to individual given amount
            if transaction.by.username != "savings":
                members[transaction.by.username]['given'] += transaction.amount # add to user given amount
                total_spend_amount += transaction.amount 

            else: 
                total_saved_amount -= transaction.amount
                total_spend_amount += transaction.amount

            # split the amount to all the shared members
            for user in transaction.share_to.all():     # for each shared member
                members[user.username]['share'] += transaction.amount / len(transaction.share_to.all()) # add to shared amount

    
    data = {}
    total_amount = 0
    for member, money in members.items():
        money['share'] = round_up(money['share'])

        data[member] = {
            'given' : money['given'],
            'share' : money['share'],
            'get' : 0,
            'pay' : 0,
        }

        total_amount += money['given']
    
    # get the active members
    active_members = [
        member.username
        for member in group.get_members
        if members[member.username]['share'] > 0
    ]
    active_members_count = len(active_members)
    if active_members_count == 0:
        # return HttpResponse("No active members")
        active_members_count = 1

    # split the total saved amount to all the active members
    savings_share_amount = round_up(total_saved_amount / active_members_count)

    # add the share amount to all the active members
    for member in active_members:
        # given + pay = share + get
        # given - share = get - pay
        # extra = given - share  = get - pay

        # data[member]['share'] += savings_share_amount
        data[member]['extra']   = data[member]['given'] - data[member]['share']

        # get_amount
        if data[member]['extra'] > 0:
            data[member]['get'] = data[member]['extra']
            data[member]['pay'] = 0
        # pay_amount
        else:
            data[member]['get'] = 0
            data[member]['pay'] = abs(data[member]['extra'])
        
        data[member].pop('extra')

    return custom_render(request, 'pages/transactions_split.html', {
        'data'                  : data,
        'total_amount'          : total_amount,
        'total_spend_amount'    : total_spend_amount,
        'total_savings'         : total_saved_amount,
        'start_point'           : start_date,
        'stop_point'            : stop_date,
        'group'                 : group,
        'title'                 : f'{group.name} Group Transactions Split'
    })

@login_required
@group_member_login_required
def recalculate_savings(request, group):
    group.update_savings_amount()
    return HttpResponse(group.savings, status = 200)