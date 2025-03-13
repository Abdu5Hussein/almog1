from django.db import transaction
from django.utils.timezone import now
from .models import EmployeesTable, SellinvoiceTable, OrderQueue, EmployeeQueue
from django_q.tasks import async_task
from datetime import timedelta
from django_q.models import Schedule
from django_q.tasks import schedule

def assign_orders():
    with transaction.atomic():
        # Get available employees from the queue in order
        available_employees = EmployeeQueue.objects.filter(is_available=True, is_assigned=False).order_by('position')

        # Get pending orders that are not assigned
        pending_orders = SellinvoiceTable.objects.filter(
            invoice_status='سلمت', delivery_status='جاري التوصيل', is_assigned=False
        ).order_by('invoice_date').select_for_update()

        if not available_employees.exists() or not pending_orders.exists():
            return

        for order in pending_orders:
            if available_employees.exists():
                employee_queue = available_employees.first()
                employee = employee_queue.employee  # Get the employee from the queue

                # Assign employee and update status
                employee.is_available = False
                employee.has_active_order = True
                employee.save()

                # Update order status
                order.delivery_status = 'جاري التوصيل'
                order.is_assigned = True
                order.save()

                # Create an entry in the order queue
                OrderQueue.objects.create(
                    employee=employee, order=order, is_accepted=False, is_assigned=True, assigned_at=now()
                )

                # Schedule confirmation check after 5 minutes
                async_task('app.tasks.check_order_confirmation', order_id=SellinvoiceTable.invoice_no)

                # Update queue: Mark employee as assigned
                employee_queue.is_assigned = True
                employee_queue.is_available = False
                employee_queue.assigned_time = now()
                employee_queue.save()

                # Remove assigned employee from available list
                available_employees = available_employees.exclude(employee=employee)
            else:
                break


def check_order_confirmation(order_id):
    expiration_time = now() - timedelta(minutes=5)
    try:
        with transaction.atomic():
            order_queue = OrderQueue.objects.select_for_update().get(order__invoice_no=order_id, is_accepted=False)

            if order_queue.assigned_at <= expiration_time:
                # Unassign the employee
                employee = order_queue.employee
                employee.is_available = True
                employee.has_active_order = False
                employee.save()

                # Mark employee queue entry as available again
                employee_queue = EmployeeQueue.objects.get(employee=employee)
                employee_queue.is_available = True
                employee_queue.is_assigned = False
                employee_queue.save()

                # Mark the order as unassigned
                order_queue.order.is_assigned = False
                order_queue.order.save()

                # Delete the queue entry
                order_queue.delete()

                # Re-run order assignment
                async_task('app.tasks.assign_orders')
    except OrderQueue.DoesNotExist:
        pass  # Ignore if the order has already been processed


# Schedule task to assign orders every 1 minute
def schedule_assign_orders():
    if not Schedule.objects.filter(func='app.tasks.assign_orders').exists():
        schedule(
            'app.tasks.assign_orders',
            schedule_type=Schedule.MINUTES,
            minutes=0.5,  # Run every 1 minute
            repeats=-1,
            next_run=now()
        )

# Schedule task to check order confirmation every 2 minutes
def schedule_background_tasks():
    if not Schedule.objects.filter(func='app.tasks.check_order_confirmation').exists():
        schedule(
            'app.tasks.check_order_confirmation',
            schedule_type=Schedule.MINUTES,
            minutes=2,  # Runs every 2 minutes
            repeats=-1,
            next_run=now()
        )
