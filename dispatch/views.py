from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import generic

from .forms import OrderForm, ConnectForm, RegularlyForm
from .models import DispatchCheck, DispatchOrderConnect, DispatchOrder, DispatchRegularly, DispatchRegularlyFixed, RegularlyGroup, DispatchRegularlyConnect
from accounting.models import Salary
from humanresource.models import Member
from vehicle.models import Vehicle

from datetime import datetime, timedelta, date
# from utill.decorator import option_year_deco

TODAY = str(datetime.now())[:10]
FORMAT = "%Y-%m-%d"
WEEK = ['(월)', '(화)', '(수)', '(목)', '(금)', '(토)', '(일)', ]
WEEK2 = ['월', '화', '수', '목', '금', '토', '일', ]

def calendar_create(request):
    if request.method == "POST":
        creator = get_object_or_404(Member, id=request.session.get('user'))
        date = request.POST.get('date', None)
        try:
            check = get_object_or_404(DispatchCheck, date=date)
            if check.member_id1:
                check.member_id2 = creator
                check.dispatch_check = 'y'
            else:
                check.member_id1 = creator
                check.dispatch_check = 'n'
                
        except:
            check = DispatchCheck(
                member_id1 = creator,
                date = date,
                dispatch_check = 'n',
                creator = creator,
            )
        check.save()
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    else:
        return HttpResponseNotAllowed(['post'])

def calendar_delete_1(request):
    if request.method == "POST":
        date = request.POST.get('date', None)
        check = get_object_or_404(DispatchCheck, date=date)
        check.member_id1 = check.member_id2
        check.member_id2 = None
        check.dispatch_check = 'n'
        check.save()

        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    else:
        return HttpResponseNotAllowed(['post'])

def calendar_delete_2(request):
    if request.method == "POST":
        date = request.POST.get('date', None)
        check = get_object_or_404(DispatchCheck, date=date)
        check.member_id2 = None
        check.dispatch_check = 'n'
        check.save()

        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    else:
        return HttpResponseNotAllowed(['post'])


class ScheduleList(generic.ListView):
    template_name = 'dispatch/schedule.html'
    context_object_name = 'vehicle_list'
    model = Vehicle

    def get_queryset(self):
        select = self.request.GET.get('select', None)
        search_d = self.request.GET.get('search_d', None)
        search_v = self.request.GET.get('search_v', None)

        if select == 'driver':
            vehicle_list = Vehicle.objects.prefetch_related('info_bus_id', 'info_regulary_bus_id').filter(driver_name__contains=search_d).filter(use='y')
        elif select == 'vehicle':
            vehicle_list = Vehicle.objects.prefetch_related('info_bus_id', 'info_regulary_bus_id').filter(vehicle_num__contains=search_v).filter(use='y')
        else:
            vehicle_list = Vehicle.objects.prefetch_related('info_bus_id', 'info_regulary_bus_id').filter(use='y')
        return vehicle_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = self.request.GET.get('date', TODAY)

        schedule_list = []

        for vehicle in context['vehicle_list']:
            temp = []
            order_list = vehicle.info_bus_id.exclude(arrival_date__lte=f'{date} 00:00').exclude(departure_date__gte=f'{date} 24:00')
            e_regulary_list = vehicle.info_regulary_bus_id.exclude(arrival_date__lte=f'{date} 00:00').exclude(departure_date__gte=f'{date} 24:00').filter(work_type='출근')
            l_regulary_list = vehicle.info_regulary_bus_id.exclude(arrival_date__lte=f'{date} 00:00').exclude(departure_date__gte=f'{date} 24:00').filter(work_type='퇴근')
            for o in order_list:
                temp.append({
                    'work_type': '일반',
                    'departure_date': o.departure_date,
                    'arrival_date': o.arrival_date,
                    'departure': o.order_id.departure,
                    'arrival': o.order_id.arrival,
                })
            for o in e_regulary_list:
                temp.append({
                    'work_type': '출근',
                    'departure_date': o.departure_date,
                    'arrival_date': o.arrival_date,
                    'departure': o.regularly_id.departure,
                    'arrival': o.regularly_id.arrival,
                })
            for o in l_regulary_list:
                temp.append({
                    'work_type': '퇴근',
                    'departure_date': o.departure_date,
                    'arrival_date': o.arrival_date,
                    'departure': o.regularly_id.departure,
                    'arrival': o.regularly_id.arrival,
                })

            schedule_list.append(temp)
        print(schedule_list)
        context['schedule_list'] = schedule_list

        context['datalist_vehicle'] = Vehicle.objects.filter(use='y')
        context['datalist_driver'] = Member.objects.filter(role='운전원')
        
        context['select'] = self.request.GET.get('select', '')
        context['search_d'] = self.request.GET.get('search_d', '')
        context['search_v'] = self.request.GET.get('search_v', '')
        context['date'] = date
        return context


class DocumentList(generic.ListView):
    template_name = 'dispatch/document.html'
    context_object_name = 'order_list'
    model = DispatchOrder

    def get_queryset(self):
        date = self.request.GET.get('date', TODAY)
        order_list = DispatchOrder.objects.prefetch_related('info_order').filter(departure_date__lte=f'{date}T24:00').filter(arrival_date__gte=f'{date}T00:00')
        return order_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        departure_date = []
        time = []
        num_days = []

        for order in context['order_list']:
            d_y = order.departure_date[0:4]
            d_m = order.departure_date[5:7]
            d_d = order.departure_date[8:10]
            d_t = order.departure_date[11:16]
            d_date = date(int(d_y), int(d_m), int(d_d))
            d_w = WEEK[d_date.weekday()]
            d_y = d_y[2:4]

            a_y = order.arrival_date[0:4]
            a_m = order.arrival_date[5:7]
            a_d = order.arrival_date[8:10]
            a_t = order.arrival_date[11:16]
            a_date = date(int(a_y), int(a_m), int(a_d))
            a_w = WEEK[d_date.weekday()]
            a_y = a_y[2:4]
            
            date_diff = (a_date - d_date) + timedelta(days=1)
            if date_diff.days > 1:
                num_days.append(date_diff.days)
            else:
                num_days.append('')

            departure_date.append(f"{d_y}.{d_m}.{d_d} {d_w}")
            time.append(f"{d_t}~{a_t}")
            # arrival_date.append(f"{a_y}.{a_m}.{a_d} {a_w} {a_t}")

        connect_list = []
        for order in context['order_list']:
            connect_list.append(order.info_order.all())
        print("CONNETCTT", connect_list)
        context['connect_list'] = connect_list
        context['departure_date'] = departure_date
        context['num_days'] = num_days
        context['time'] = time
        context['date'] = self.request.GET.get('date', TODAY)
        
        return context
    
class RegularlyDispatchList(generic.ListView):
    template_name = 'dispatch/regularly.html'
    context_object_name = 'order_list'
    model = DispatchRegularly

    def get_queryset(self):
        group = self.request.GET.get('group', '')
        date = self.request.GET.get('date', TODAY)

        weekday = WEEK2[datetime.strptime(date, FORMAT).weekday()]

        dispatch_list = []
        group_data = None
        
        if group:
            group_data = RegularlyGroup.objects.get(name=group)
            dispatch_list = group_data.regularly_info.filter(week__contains=weekday).order_by('number1', 'number2')
        else:
            dispatch_list = DispatchRegularly.objects.filter(week__contains=weekday).order_by('group', 'number1', 'number2')

            print("AAAA", dispatch_list)
        return dispatch_list


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ############### 스케줄 부분
        date = self.request.GET.get('date', TODAY)

        # schedule_list = []
        # vehicle_list = Vehicle.objects.prefetch_related('info_bus_id', 'info_regulary_bus_id').filter(use='y')
        # for vehicle in vehicle_list:
        #     temp = []
        #     order_list = vehicle.info_bus_id.exclude(arrival_date__lte=f'{date} 00:00').exclude(departure_date__gte=f'{date} 24:00')
        #     e_regulary_list = vehicle.info_regulary_bus_id.exclude(arrival_date__lte=f'{date} 00:00').exclude(departure_date__gte=f'{date} 24:00').filter(work_type='출근')
        #     l_regulary_list = vehicle.info_regulary_bus_id.exclude(arrival_date__lte=f'{date} 00:00').exclude(departure_date__gte=f'{date} 24:00').filter(work_type='퇴근')
        #     for o in order_list:
        #         temp.append({
        #             'work_type': '일반',
        #             'departure_date': o.departure_date,
        #             'arrival_date': o.arrival_date,
        #             'departure': o.order_id.departure,
        #             'arrival': o.order_id.arrival,
        #         })
        #     for o in e_regulary_list:
        #         temp.append({
        #             'work_type': '출근',
        #             'departure_date': o.departure_date,
        #             'arrival_date': o.arrival_date,
        #             'departure': o.regularly_id.departure,
        #             'arrival': o.regularly_id.arrival,
        #         })
        #     for o in l_regulary_list:
        #         temp.append({
        #             'work_type': '퇴근',
        #             'departure_date': o.departure_date,
        #             'arrival_date': o.arrival_date,
        #             'departure': o.regularly_id.departure,
        #             'arrival': o.regularly_id.arrival,
        #         })

        #     schedule_list.append(temp)
        # print(schedule_list)
        # context['schedule_list'] = schedule_list

        # context['datalist_vehicle'] = Vehicle.objects.filter(use='y')
        # context['datalist_driver'] = Member.objects.filter(role='운전원')
        ############
        
        # group = self.request.GET.get('group', '')
        # # 노선 클릭하면 get으로 route id 보냄
        # route = self.request.GET.get('route', '')
        
        
        # context['group_list'] = RegularlyGroup.objects.all()
        # context['group'] = group
        # context['route'] = route
        # context['date'] = date

        # # vehicle_list = Vehicle.objects.prefetch_related('info_regulary_bus_id', 'info_bus_id').filter(use='y')

        # ################# 위쪽 2주치 달력
        # date_date = datetime.strptime(date, FORMAT)
        # if date_date.weekday() != 6:
        #     first_date = date_date - timedelta(days=date_date.weekday() + 1)
        # else:
        #     first_date = date_date

        # if route:
        #     route_id = get_object_or_404(DispatchRegularly, id=route)

        #     calendar_connect_list = []
        #     calendar_date_list = []
        #     for i in range(14):
        #         cur_date = datetime.strftime(first_date + timedelta(days=i), FORMAT)
        #         calendar_date_list.append(cur_date)
        #         try:
        #             connect = DispatchRegularlyConnect.objects.filter(regularly_id=route_id).get(departure_date__startswith=cur_date)
        #             calendar_connect_list.append(connect)
        #         except DispatchRegularlyConnect.DoesNotExist:
        #             calendar_connect_list.append('')
            
        #     print("Calendar connect", calendar_connect_list)
        #     print("Calendar date", calendar_date_list)
        #     context['calendar_connect_list'] = calendar_connect_list
        #     context['calendar_date_list'] = calendar_date_list
        # ####################

        # r_enter_cnt = []
        # r_leave_cnt = []
        # order_cnt = []

        # vehicle_connect = {}
        # for vehicle in vehicle_list:
        #     r_enter_cnt.append(vehicle.info_regulary_bus_id.filter(departure_date__lte=f'{date} 24:00').filter(arrival_date__gte=f'{date} 00:00').filter(work_type="출근").count())
        #     r_leave_cnt.append(vehicle.info_regulary_bus_id.filter(departure_date__lte=f'{date} 24:00').filter(arrival_date__gte=f'{date} 00:00').filter(work_type="퇴근").count())
        #     order_cnt.append(vehicle.info_bus_id.filter(departure_date__lte=f'{date} 24:00').filter(arrival_date__gte=f'{date} 00:00').count())
            
        #     vehicle_connect[vehicle.id] = []

        # context['r_enter_cnt'] = r_enter_cnt
        # context['r_leave_cnt'] = r_leave_cnt
        # context['order_cnt'] = order_cnt
        # # context['vehicle_list'] = vehicle_list

        # connect_list = []
        # for order in context['order_list']:
        #     connect_list.append(order.info_regularly.filter(departure_date__lte=f'{date} 24:00').filter(arrival_date__gte=f'{date} 00:00'))
        #     for o in order.info_regularly.filter(departure_date__startswith=date):
        #         vehicle_connect[o.bus_id.id].append([o.departure_date, o.arrival_date])
        # context['connect_list'] = connect_list

        # order_list = DispatchOrderConnect.objects.exclude(arrival_date__lte=f'{date}T00:00').exclude(departure_date__gte=f'{date}T24:00')
        # for order in order_list:
        #     vehicle_connect[order.bus_id.id].append([order.departure_date, order.arrival_date])

        # context['vehicle_connect'] = vehicle_connect

        # bus_cnt_list = []
        # for order in context['order_list']:
        #     bus_cnt_list.append(order.info_regularly.filter(departure_date__startswith=date).count())
        # context['bus_cnt_list'] = bus_cnt_list



        return context

def regularly_fixed_create(request):
    if request.method == "POST":
        id = request.POST.get('id')
        regularly = get_object_or_404(DispatchRegularly, id=id)
        regularly.info_regularly_fixed.all().delete()
        for i in range(7):
            bus_id = request.POST.get(f'bus{i+1}')
            driver_id = request.POST.get(f'driver{i+1}')
            print("driver", driver_id)
            print("bus", bus_id)
            print("IIII", i)
            if i == 0:
                week = '일'
            elif i == 1:
                week = '월'
            elif i == 2:
                week = '화'
            elif i == 3:
                week = '수'
            elif i == 4:
                week = '목'
            elif i == 5:
                week = '금'
            elif i == 6:
                week = '토'
            
            if bus_id and driver_id:
                bus = get_object_or_404(Vehicle, id=bus_id)
                driver = get_object_or_404(Member, id=driver_id)
                fixed = DispatchRegularlyFixed(
                    regularly_id = regularly,
                    bus_id = bus,
                    driver_id = driver,
                    week = week
                )
                fixed.save()
                print("fixedd", fixed, i)
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    else:
        return HttpResponseNotAllowed(['post'])

def regularly_connect_create(request):
    if request.method == "POST":
        creator = get_object_or_404(Member, id=request.session.get('user'))
        order = get_object_or_404(DispatchRegularly, id=request.POST.get('id', None))
        bus_list = request.POST.getlist('vehicle')
        date = request.POST.get('date', None)

        connect = order.info_regularly.filter(departure_date__startswith=date)
        connect.delete()

        for bus in bus_list:
            
            vehicle = Vehicle.objects.get(id=bus)
            r_connect = DispatchRegularlyConnect(
                regularly_id = order,
                bus_id = vehicle,
                driver_id = vehicle.driver,
                departure_date = f'{date} {order.departure_time}',
                arrival_date = f'{date} {order.arrival_time}',
                work_type = order.work_type,
                driver_allowance = order.driver_allowance,
                creator = creator
            )
            r_connect.save()
            

        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    else:
        return HttpResponseNotAllowed(['post'])

class RegularlyRouteList(generic.ListView):
    template_name = 'dispatch/regularly_route.html'
    context_object_name = 'order_list'
    # paginate_by = 10
    model = DispatchRegularly

    def get_queryset(self):
        group = self.request.GET.get('group', '')
        route = self.request.GET.get('route', '')
        dispatch_list = []
        group_data = None
        if route or group:
            if group:
                group_data = RegularlyGroup.objects.get(name=group)
                dispatch_list = group_data.regularly_info.all().order_by('group', 'number1', 'number2')
            if route:
                if group_data:
                    dispatch_list = group_data.regularly_info.filter(route__contains=route).order_by('group', 'number1', 'number2')
                else:
                    dispatch_list = DispatchRegularly.objects.filter(route__contains=route).order_by('group', 'number1', 'number2')
        else:
            dispatch_list = DispatchRegularly.objects.all().order_by('group', 'number1', 'number2')
        return dispatch_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['vehicle_list'] = Vehicle.objects.all().values_list('id', 'vehicle_num', 'driver', 'driver_name').union(DispatchRegularlyFixed.objects.all().values_list('bus_id', 'bus_id__vehicle_num', 'driver_id', 'driver_id__name')).order_by('vehicle_num', 'driver_name')
        old_bus_id = context['vehicle_list'][0][0]
        bus_dict = {}
        driver_dict = {}
        for vehicle in context['vehicle_list']:
            if old_bus_id != vehicle[0]:
                bus_dict[old_bus_id] = driver_dict
                old_bus_id = vehicle[0]
                driver_dict = {}

            bus = get_object_or_404(Vehicle, id=vehicle[0])
            driver = get_object_or_404(Member, id=vehicle[2])
            
            fixed_list = DispatchRegularlyFixed.objects.select_related('regularly_id').filter(bus_id=bus).filter(driver_id=driver)
            temp = []
            for fixed in fixed_list:
                dispatch = fixed.regularly_id
                temp.append({
                    'work_type': dispatch.work_type,
                    'departure_time': dispatch.departure_time,
                    'arrival_time': dispatch.arrival_time,
                    'departure': dispatch.departure,
                    'arrival': dispatch.arrival,
                    'week': fixed.week,
                })
            driver_dict[driver.id] = temp
            # print("DRIVERDICT", driver_dict)
            if vehicle == context['vehicle_list'][len(context['vehicle_list']) - 1]:
                bus_dict[bus.id] = driver_dict
        
        print('bus_dict', bus_dict)
        context['bus_dict'] = bus_dict

        id = self.request.GET.get('id')
        if id:
            context['regularly'] = get_object_or_404(DispatchRegularly, id=id)
            connect = []
            for fixed in context['regularly'].info_regularly_fixed.all():
                connect.append({
                    'week': fixed.week,
                    'bus_id': fixed.bus_id.id,
                    'bus': fixed.bus_id.vehicle_num,
                    'driver_id': fixed.driver_id.id,
                    'driver': fixed.driver_id.name,
                })
            context['connect_list'] = connect
        context['group_list'] = RegularlyGroup.objects.all().order_by('number', 'name')
        context['vehicles'] = Vehicle.objects.filter(use='y')
        driver_list = Member.objects.filter(role='운전원').values_list('id', 'name')
        context['driver_dict'] = {}
        for driver in driver_list:
            context['driver_dict'][driver[0]] = driver[1]
        return context

def regularly_order_create(request):
    context = {}
    if request.method == "POST":
        creator = get_object_or_404(Member, pk=request.session.get('user'))
        order_form = RegularlyForm(request.POST)
        print("RRRR", request.POST)

        if order_form.is_valid():
            print("VALID")
            # if datetime.strptime(request.POST.get('contract_start_date'), FORMAT) > datetime.strptime(request.POST.get('contract_end_date'), FORMAT):
            #     context = {}
            #     # context['order_list'] = DispatchOrder.objects.exclude(regularly=None).order_by('-pk')
            #     context['group_list'] = RegularlyGroup.objects.all()
            #     # context['error'] = "출발일이 도착일보다 늦습니다"
            #     #raise BadRequest('출발일이 도착일보다 늦습니다.')
            #     #return render(request, 'dispatch/regularly_order_create.html', context)
            #     raise Http404
            post_group = request.POST.get('group', None)
            try:
                regularly_group = RegularlyGroup.objects.get(pk=post_group)
            except Exception as e:
                regularly_group = None

            week = ' '.join(request.POST.getlist('week', None))
            # regularly = RegularlyOrder(
            #     week=week,
            #     term_begin=request.POST.get('term_begin', None),
            #     term_end=request.POST.get('term_end', None),
            #     regularly_group=regularly_group,
            # )
            # regularly.save()
            
            order = order_form.save(commit=False)
            order.price = int(order_form.cleaned_data['price'].replace(',',''))
            order.driver_allowance = int(order_form.cleaned_data['driver_allowance'].replace(',',''))
            order.week = week
            order.creator = creator
            order.group = regularly_group
            order.route = order_form.cleaned_data['departure'] + " ▶ " + order_form.cleaned_data['arrival']
            order.departure_time = request.POST.get('departure_time1') + ":" + request.POST.get('departure_time2')
            order.arrival_time = request.POST.get('arrival_time1') + ":" + request.POST.get('arrival_time2')
            order.save()
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        else:
            raise Http404
    else:
        return HttpResponseNotAllowed(['post'])

def regularly_order_edit_check(request):
    if request.method == 'POST':
        departure_time = f'{request.POST.get("departure_time1")}:{request.POST.get("departure_time2")}'
        arrival_time = f'{request.POST.get("arrival_time1")}:{request.POST.get("arrival_time2")}'
        id = request.POST.get('id')
        print(id)
        regularly = get_object_or_404(DispatchRegularly, id=id)
        fixed_list = regularly.info_regularly_fixed.select_related('regularly_id').all()

        for fixed in fixed_list:
            bus = fixed.bus_id
            driver = fixed.driver_id
            week = fixed.week
            
            r_bus_list = DispatchRegularlyFixed.objects.select_related('regularly_id').filter(bus_id=bus).filter(week=week)
            r_driver_list = DispatchRegularlyFixed.objects.select_related('regularly_id').filter(driver_id=driver).filter(week=week)
            for r in r_bus_list:
                if r.regularly_id == regularly:
                    continue
                if not (r.regularly_id.arrival_time < departure_time or r.regularly_id.departure_time > arrival_time):
                    print("BUSLIST", r)
                    return JsonResponse({
                        'status': 'false',
                        'week': f'({week})',
                        'route': r.regularly_id.route,
                        'driver': r.driver_id.name,
                        'bus': r.bus_id.vehicle_num,
                        'arrival_time': r.regularly_id.arrival_time,
                        'departure_time': r.regularly_id.departure_time,
                        })
            for r in r_driver_list:
                if r.regularly_id == regularly:
                    continue
                print("week", r.week, week)
                if not (r.regularly_id.arrival_time < departure_time or r.regularly_id.departure_time > arrival_time):
                    print("driver", r)
                    
                    return JsonResponse({
                        'status': 'false',
                        'week': f'({week})',
                        'route': r.regularly_id.route,
                        'driver': r.driver_id.name,
                        'bus': r.bus_id.vehicle_num,
                        'arrival_time': r.regularly_id.arrival_time,
                        'departure_time': r.regularly_id.departure_time,
                        })
        return JsonResponse({'status': 'true'})
    else:
        return HttpResponseNotAllowed(['post'])

def regularly_order_edit(request):
    id = request.POST.get('id', None)
    order = get_object_or_404(DispatchRegularly, pk=id)
    
    if request.method == 'POST':
        creator = get_object_or_404(Member, pk=request.session.get('user'))
        order_form = RegularlyForm(request.POST)
        if order_form.is_valid():
            # overlap = ''
            # overlap_list = DispatchRegularly.objects.exclude(departure_time__gt=order.arrival_time).exclude(arrival_time__lt=order.departure_time)
            # for dispatch in overlap_list:
            #     for i in order.week.split(" "):
            #         try:
            #             temp = dispatch.info_regularly_fixed.get(week=i)
            #             bus = temp.bus_id
            #             driver = temp.driver_id
            #             cur = order.info_regularly_fixed.get(week=i)
            #         except DispatchRegularlyFixed.DoesNotExist:
            #             continue

                    
            #         if bus == cur.bus_id or driver == cur.driver_id:
            #             overlap = dispatch
            # print("OVERLAP", overlap)

            group = get_object_or_404(RegularlyGroup, pk=request.POST.get('group'))
            week = ' '.join(request.POST.getlist('week', None))
        
            # if datetime.strptime(request.POST.get('contract_start_date'), FORMAT) > datetime.strptime(request.POST.get('contract_end_date'), FORMAT):
            #     #raise BadRequest('출발일이 도착일보다 늦습니다.')
            #     raise Http404
            
            # route_name = order_form.cleaned_data['departure'] + " ▶ " + order_form.cleaned_data['arrival']
            departure_time1 = request.POST.get('departure_time1')
            departure_time2 = request.POST.get('departure_time2')
            arrival_time1 = request.POST.get('arrival_time1')
            arrival_time2 = request.POST.get('arrival_time2')

            if len(departure_time1) < 2:
                departure_time1 = f'0{departure_time1}'
            if len(departure_time2) < 2:
                departure_time2 = f'0{departure_time2}'
            if len(arrival_time1) < 2:
                arrival_time1 = f'0{arrival_time1}'
            if len(arrival_time2) < 2:
                arrival_time2 = f'0{arrival_time2}'

            order.references = order_form.cleaned_data['references']
            order.departure = order_form.cleaned_data['departure']
            order.arrival = order_form.cleaned_data['arrival']
            order.departure_time = f'{departure_time1}:{departure_time2}'
            order.arrival_time = f'{arrival_time1}:{arrival_time2}'
            # order.bus_type = order_form.cleaned_data['bus_type']
            # order.bus_cnt = order_form.cleaned_data['bus_cnt']
            order.price = int(order_form.cleaned_data['price'].replace(',',''))
            order.driver_allowance = int(order_form.cleaned_data['driver_allowance'].replace(',',''))
            order.number1 = order_form.cleaned_data['number1']
            order.number2 = order_form.cleaned_data['number2']
            # order.customer = order_form.cleaned_data['customer']
            # order.customer_phone = order_form.cleaned_data['customer_phone']
            # order.contract_start_date = order_form.cleaned_data['contract_start_date']
            # order.contract_end_date = order_form.cleaned_data['contract_end_date']
            order.work_type = order_form.cleaned_data['work_type']

            order.week = week
            order.route = request.POST.get('route')
            order.group = group
            order.creator = creator
            order.save()

            order.info_regularly_fixed.exclude(week__in=request.POST.getlist('week')).delete()

            
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        else: 
            raise Http404
    else:
        return HttpResponseNotAllowed(['post'])

def regularly_order_delete(request):
    if request.method == "POST":
        id = request.POST.get("id")
        
        order = get_object_or_404(DispatchRegularly, pk=id)
        order.delete()
        return redirect('dispatch:regularly_route')
    else:
        return HttpResponseNotAllowed(['post'])

def regularly_group_create(request):
    if request.method == "POST":
        group = RegularlyGroup(
            name = request.POST.get('name'),
            number = request.POST.get('number'),
            creator = get_object_or_404(Member, pk=request.session['user'])
        )
        group.save()
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    else:
        return HttpResponseNotAllowed(['POST'])

def regularly_group_edit(request):

    if request.method == "POST":
        id = request.POST.get('id', None)
        name = request.POST.get('name', None)
        num = request.POST.get('number', None)
        group = get_object_or_404(RegularlyGroup, id=id)
        
        group.number = num
        group.name = name
        group.save()
        
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    else:
        return HttpResponseNotAllowed(['POST'])

def regularly_group_delete(request):
    if request.method == "POST":
        group = get_object_or_404(RegularlyGroup, id=request.POST.get('id', None))
        group.delete()
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    else:
        return HttpResponseNotAllowed(['POST'])

class OrderList(generic.ListView):
    template_name = 'dispatch/order.html'
    context_object_name = 'order_list'
    model = DispatchOrder
    paginate_by = 10

    def get_queryset(self):
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        route = self.request.GET.get('route')
        customer = self.request.GET.get('customer')
        # self.next_week = (datetime.strptime(TODAY, FORMAT) + timedelta(days=7)).strftime(FORMAT)

        if start_date or end_date or route or customer:
            dispatch_list = []
            if start_date and end_date:
                dispatch_list = DispatchOrder.objects.prefetch_related('info_order').exclude(arrival_date__lt=f'{start_date}T00:00').exclude(departure_date__gt=f'{end_date}T24:00').order_by('departure_date')
                # dispatch_list = DispatchOrder.objects.filter(departure_date__range=[start_date + "T00:00", end_date + "T24:00"]).order_by('departure_date')
            if route:
                if dispatch_list:
                    dispatch_list = dispatch_list.filter(route__contains=route).order_by('departure_date')
                else:
                    dispatch_list = DispatchOrder.objects.prefetch_related('info_order').filter(route__contains=route).order_by('departure_date')
            if customer:
                if dispatch_list:
                    dispatch_list = dispatch_list.filter(customer__contains=customer).order_by('departure_date')
                else:
                    dispatch_list = DispatchOrder.objects.prefetch_related('info_order').filter(customer__contains=customer).order_by('departure_date')
        else:
            
            dispatch_list = DispatchOrder.objects.prefetch_related('info_order').exclude(arrival_date__lt=f'{TODAY}T00:00').exclude(departure_date__gt=f'{TODAY}T24:00').order_by('departure_date')
        
        return dispatch_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_numbers_range = 5
        max_index = len(paginator.page_range)
        page = self.request.GET.get('page')
        current_page = int(page) if page else 1

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index
        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range
        
        #페이징 끝
        # departure_date = []
        # time = []
        # num_days = []

        # for order in context['order_list']:
        #     d_y = order.departure_date[0:4]
        #     d_m = order.departure_date[5:7]
        #     d_d = order.departure_date[8:10]
        #     d_t = order.departure_date[11:16]
        #     d_date = date(int(d_y), int(d_m), int(d_d))
        #     d_w = WEEK[d_date.weekday()]
        #     d_y = d_y[2:4]

        #     a_y = order.arrival_date[0:4]
        #     a_m = order.arrival_date[5:7]
        #     a_d = order.arrival_date[8:10]
        #     a_t = order.arrival_date[11:16]
        #     a_date = date(int(a_y), int(a_m), int(a_d))
        #     a_w = WEEK[d_date.weekday()]
        #     a_y = a_y[2:4]
            
        #     date_diff = (a_date - d_date) + timedelta(days=1)
        #     if date_diff.days > 1:
        #         num_days.append(date_diff.days)
        #     else:
        #         num_days.append('')

        #     departure_date.append(f"{d_y}.{d_m}.{d_d} {d_w}")
        #     time.append(f"{d_t}~{a_t}")
        #     # arrival_date.append(f"{a_y}.{a_m}.{a_d} {a_w} {a_t}")

        # context['departure_date'] = departure_date
        # context['num_days'] = num_days
        # context['time'] = time
        # context['route_old'] = self.request.GET.get('route', '')
        # context['customer_old'] = self.request.GET.get('customer', '')
        # start_date_old = self.request.GET.get('start_date', TODAY)
        # context['start_date_old'] = start_date_old
        # end_date_old = self.request.GET.get('end_date', TODAY)
        # context['end_date_old'] = end_date_old

        # vehicle_list = Vehicle.objects.prefetch_related('info_regulary_bus_id', 'info_bus_id').filter(use='y')

        # r_enter_cnt = []
        # r_leave_cnt = []
        # order_cnt = []
        # # 
        # vehicle_connect = {}
            
        # for vehicle in vehicle_list:
        #     if start_date_old == end_date_old:
        #         r_enter_cnt.append(vehicle.info_regulary_bus_id.filter(departure_date__lte=f'{start_date_old} 24:59').filter(arrival_date__gte=f'{start_date_old} 00:00').filter(work_type="출근").count())
        #         r_leave_cnt.append(vehicle.info_regulary_bus_id.filter(departure_date__lte=f'{start_date_old} 24:59').filter(arrival_date__gte=f'{start_date_old} 00:00').filter(work_type="퇴근").count())
        #         order_cnt.append(vehicle.info_bus_id.filter(departure_date__lte=f'{start_date_old} 24:59').filter(arrival_date__gte=f'{start_date_old} 00:00').count())

        #     # 
        #     vehicle_connect[vehicle.id] = []

        # context['r_enter_cnt'] = r_enter_cnt
        # context['r_leave_cnt'] = r_leave_cnt
        # context['order_cnt'] = order_cnt
        # context['vehicle_list'] = vehicle_list

        # print("et", r_enter_cnt)
        # print("lt", r_leave_cnt)
        # print("ot", order_cnt)

        # connect_list = []
        # min_date = f'{start_date_old}T23:59'
        # max_date = f'{end_date_old}T00:00'
        # for order in context['order_list']:
        #     connect_list.append(order.info_order.all())

        #     if order.departure_date < min_date:
        #         min_date = order.departure_date
        #     if order.arrival_date > max_date:
        #         max_date = order.arrival_date
        # context['connect_list'] = connect_list

        # min_date = f'{min_date[:10]}T00:00'
        # max_date = f'{max_date[:10]}T24:00'

        # print("MIN", min_date, "max", max_date)
        # order_connect_range = DispatchOrderConnect.objects.exclude(arrival_date__lt=min_date).exclude(departure_date__gt=max_date)
        # for o in order_connect_range:
        #     vehicle_connect[o.bus_id.id].append([o.departure_date, o.arrival_date])
            
        
        # regularly_order_list = DispatchRegularlyConnect.objects.filter(departure_date__range=[f'{min_date[:10]} {min_date[11:]}', f'{max_date[:10]} {max_date[11:]}'])
        # print("REGURLRLRY", regularly_order_list)
        # for regularly in regularly_order_list:
        #     vehicle_connect[regularly.bus_id.id].append([regularly.departure_date, regularly.arrival_date])

        # context['vehicle_connect'] = vehicle_connect
        return context

def order_connect_create(request):
    if request.method == "POST":
        creator = get_object_or_404(Member, id=request.session.get('user'))
        order = get_object_or_404(DispatchOrder, id=request.POST.get('id', None))
        bus_list = request.POST.getlist('vehicle')
        
        connect = order.info_order.all()
        connect.delete()

        for bus in bus_list:
            vehicle = Vehicle.objects.get(id=bus)
            connect = DispatchOrderConnect(
                order_id = order,
                bus_id = vehicle,
                driver_id = vehicle.driver,
                departure_date = order.departure_date,
                arrival_date = order.arrival_date,
                driver_allowance = order.driver_allowance,
                creator = creator
            )
            connect.save()
        
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

    else:
        return HttpResponseNotAllowed(['post'])


def order_create(request):    
    if request.method == "POST":
        creator = get_object_or_404(Member, pk=request.session.get('user'))
        order_form = OrderForm(request.POST)
        print("POST", request.POST)
        if order_form.is_valid():
            post_departure_date = request.POST.get('departure_date', None).replace('T', ' ')
            post_arrival_date = request.POST.get('arrival_date', None).replace('T', ' ')

            format = '%Y-%m-%d %H:%M'
            if datetime.strptime(post_departure_date, format) > datetime.strptime(post_arrival_date, format):
                print("term begin > term end")
                raise Http404

            order = order_form.save(commit=False)
            order.price = int(order_form.cleaned_data['price'].replace(',',''))
            order.driver_allowance = int(order_form.cleaned_data['driver_allowance'].replace(',',''))
            order.VAT = request.POST.get('VAT', 'n')
            order.payment_method = request.POST.get('payment_method', 'n')
            order.creator = creator
            order.route = order_form.cleaned_data['departure'] + " ▶ " + order_form.cleaned_data['arrival']

            order.save()
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        else:
            raise Http404
    else:
        return HttpResponseNotAllowed(['post'])

def order_edit_check(request):
    pk = request.POST.get('id')
    order = get_object_or_404(DispatchOrder, pk=pk)
    #
    connects = order.info_order.all()
    # r_connects = order.info_regularly.all()
    for connect in connects:
        bus = connect.bus_id
        # r_connects = bus.info_regulary_bus_id.all()

        post_departure_date = request.POST.get('departure_date', None)
        post_arrival_date = request.POST.get('arrival_date', None)

        format = '%Y-%m-%d %H:%M'
        if datetime.strptime(post_departure_date.replace('T', ' '), format) > datetime.strptime(post_arrival_date.replace('T', ' '), format):
            print("term begin > term end")
            raise Http404
        
        if bus.info_bus_id.exclude(arrival_date__lt=post_departure_date).exclude(departure_date__gt=post_arrival_date).exclude(id__in=connects):
            return JsonResponse({"status": "fail"})
        if bus.info_regulary_bus_id.exclude(arrival_date__lt=post_departure_date).exclude(departure_date__gt=post_arrival_date):
            return JsonResponse({"status": "fail"})
    
    return JsonResponse({'status': 'success'})

def order_edit(request):
    pk = request.POST.get('id')
    order = get_object_or_404(DispatchOrder, pk=pk)
    
    if request.method == 'POST':
        creator = get_object_or_404(Member, pk=request.session.get('user'))
        order_form = OrderForm(request.POST)

        if order_form.is_valid():
            post_departure_date = request.POST.get('departure_date', None)
            post_arrival_date = request.POST.get('arrival_date', None)

            format = '%Y-%m-%d %H:%M'
            if datetime.strptime(post_departure_date.replace('T', ' '), format) > datetime.strptime(post_arrival_date.replace('T', ' '), format):
                print("term begin > term end")
                raise Http404

            #
            connects = order.info_order.all()
            
            for connect in connects:
                bus = connect.bus_id
                if bus.info_bus_id.exclude(arrival_date__lt=post_departure_date).exclude(departure_date__gt=post_arrival_date).exclude(id__in=connects):
                    return JsonResponse({"status": "fail"})
                if bus.info_regulary_bus_id.exclude(arrival_date__lt=post_departure_date).exclude(departure_date__gt=post_arrival_date):
                    return JsonResponse({"status": "fail"})

            for connect in connects:
                connect.departure_date = post_departure_date
                connect.arrival_date = post_arrival_date
                connect.save()
            #

            order.operation_type = order_form.cleaned_data['operation_type']
            order.references = order_form.cleaned_data['references']
            order.departure = order_form.cleaned_data['departure']
            order.arrival = order_form.cleaned_data['arrival']
            order.departure_date = order_form.cleaned_data['departure_date']
            order.arrival_date = order_form.cleaned_data['arrival_date']
            order.bus_type = order_form.cleaned_data['bus_type']
            order.bus_cnt = order_form.cleaned_data['bus_cnt']
            order.price = int(order_form.cleaned_data['price'].replace(',',''))
            order.driver_allowance = int(order_form.cleaned_data['driver_allowance'].replace(',',''))
            order.contract_status = order_form.cleaned_data['contract_status']
            order.cost_type = order_form.cleaned_data['cost_type']
            order.customer = order_form.cleaned_data['customer']
            order.customer_phone = order_form.cleaned_data['customer_phone']
            order.deposit_status = order_form.cleaned_data['deposit_status']
            order.deposit_date = order_form.cleaned_data['deposit_date']
            order.bill_date = order_form.cleaned_data['bill_date']
            order.collection_type = order_form.cleaned_data['collection_type']
            
            order.payment_method = request.POST.get('payment_method', 'n')
            order.VAT = request.POST.get('VAT', 'n')
            order.route = order_form.cleaned_data['departure'] + " ▶ " + order_form.cleaned_data['arrival']
            order.creator = creator
            print("ORDER", order)
            order.save()

            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        else:
            raise Http404
    else:
        return HttpResponseNotAllowed(['post'])

def order_delete(request):
    if request.method == "POST":
        id_list = request.POST.getlist('id', None)
        for id in id_list:
            order = get_object_or_404(DispatchOrder, id=id)
            order.delete()

        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    else:
        return HttpResponseNotAllowed(['post'])

def line_print(request):
    context = {}
    date = request.GET.get('date')
    week = WEEK[datetime.strptime(date, FORMAT).weekday()][1]
    
    
    regularly_list = DispatchRegularly.objects.prefetch_related('info_regularly').exclude(info_regularly=None).filter(week__contains=week).order_by('group', 'number1', 'number2', 'departure_time')
    print(regularly_list)
    temp = []
    temp2 = []
    group = ''
    context['regularly_list'] = []
    context['connect_list'] = []
    for r in regularly_list:
        print("GROUP", r.group.name)
        if r.group.name != group:
            group = r.group.name
            if r != regularly_list[0]:
                context['regularly_list'].append(temp)
                context['connect_list'].append(temp2)
                temp = []
                temp2 = []
        temp.append(r)
        temp2.append(r.info_regularly.filter(departure_date__startswith=date))

    if r == regularly_list[len(regularly_list)-1]:
        context['regularly_list'].append(temp)
        context['connect_list'].append(temp2)

        
        
    no_list = DispatchRegularly.objects.filter(info_regularly=None).order_by('group', 'number1', 'number2', 'departure_time')
    
    print('REGULSRY', context['regularly_list'])
    print('connect_list', context['connect_list'])
    context['no_list'] = no_list

    return render(request, 'dispatch/line_print.html', context)

def bus_print(request):
    context = {}
    date = request.GET.get('date')

    vehicle_list = Vehicle.objects.filter(use='y').order_by('vehicle_num')
    context['vehicle_list'] = vehicle_list
    
    connect_object = {}
    e_connect_object = {}
    c_connect_object = {}
    for vehicle in vehicle_list:
        connect_object[vehicle.id] = []
        e_connect_object[vehicle.id] = []
        c_connect_object[vehicle.id] = []

    r_connect_list = DispatchRegularlyConnect.objects.select_related('bus_id', 'regularly_id').filter(departure_date__startswith=date).order_by('departure_date')
    for connect in r_connect_list:
        if connect.work_type == "출근":
            e_connect_object[connect.bus_id.id].append(connect)
        elif connect.work_type == "퇴근":
            c_connect_object[connect.bus_id.id].append(connect)

    connect_list = DispatchOrderConnect.objects.select_related('bus_id', 'order_id').filter(departure_date__lte=f'{date}T24:00').filter(arrival_date__gte=f'{date}T00:00')
    print("CONNECTSLIST", connect_list)
    for connect in connect_list:
        connect_object[connect.bus_id.id].append(connect)


    context['connect_object'] = connect_object
    context['e_connect_object'] = e_connect_object
    context['c_connect_object'] = c_connect_object
    return render(request, 'dispatch/bus_print.html', context)

def daily_driving_list(request):
    context = {}
    date = request.GET.get('date')

    vehicle_list = Vehicle.objects.filter(use='y').order_by('vehicle_num')
    context['vehicle_list'] = vehicle_list
    
    connect_object = {}
    e_connect_object = {}
    c_connect_object = {}
    for vehicle in vehicle_list:
        connect_object[vehicle.id] = []
        e_connect_object[vehicle.id] = []
        c_connect_object[vehicle.id] = []

    r_connect_list = DispatchRegularlyConnect.objects.select_related('bus_id', 'regularly_id').filter(departure_date__startswith=date).order_by('departure_date')
    for connect in r_connect_list:
        if connect.work_type == "출근":
            e_connect_object[connect.bus_id.id].append(connect)
        elif connect.work_type == "퇴근":
            c_connect_object[connect.bus_id.id].append(connect)

    connect_list = DispatchOrderConnect.objects.select_related('bus_id', 'order_id').filter(departure_date__lte=f'{date}T24:00').filter(arrival_date__gte=f'{date}T00:00')
    print("CONNECTSLIST", connect_list)
    for connect in connect_list:
        connect_object[connect.bus_id.id].append(connect)


    context['connect_object'] = connect_object
    context['e_connect_object'] = e_connect_object
    context['c_connect_object'] = c_connect_object
    return render(request, 'dispatch/daily_driving_list.html', context)

def daily_driving_print(request):
    id_list = request.GET.get('id').split(',')
    date = request.GET.get('date')
    context = {}
    context['vehicle_list'] = []
    context['order_list'] = []
    context['e_order_list'] = []
    context['c_order_list'] = []
    context['cnt'] = len(id_list)
    context['date'] = date

    for id in id_list:
        if id and date:
            vehicle = get_object_or_404(Vehicle, id=id)
            context['vehicle_list'].append(vehicle)
            context['order_list'].append(DispatchOrderConnect.objects.select_related('order_id').filter(departure_date__lte=f'{date}T24:00').filter(arrival_date__gte=f'{date}T00:00').filter(bus_id=vehicle).order_by('departure_date'))
            context['e_order_list'].append(DispatchRegularlyConnect.objects.select_related('regularly_id').filter(departure_date__startswith=date).filter(work_type="출근").filter(bus_id=vehicle).order_by('departure_date'))
            context['c_order_list'].append(DispatchRegularlyConnect.objects.select_related('regularly_id').filter(departure_date__startswith=date).filter(work_type="퇴근").filter(bus_id=vehicle).order_by('departure_date'))
            print("ENETET", context['e_order_list'])

        else:
            raise Http404



    return render(request, 'dispatch/daily_driving_print.html', context)
    

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@