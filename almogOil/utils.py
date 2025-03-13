from django.utils.timezone import now
from .models import EmployeeQueue, OrderQueue
from django.utils.timezone import now, timedelta

def assign_order_to_next_employee():
    # Get the first available employee who has no active order
    employee_queue = EmployeeQueue.objects.filter(
        is_available=True, is_assigned=False
    ).order_by('position').first()

    if not employee_queue:
        return None  # No available employee

    # Assign order to this employee
    employee_queue.is_assigned = True
    employee_queue.assigned_time = now()
    employee_queue.save()

    return employee_queue.employee  # Return assigned employee

def reassign_if_not_accepted():
    timeout = now() - timedelta(minutes=5)
    expired_assignments = EmployeeQueue.objects.filter(
        is_assigned=True, assigned_time__lte=timeout
    )

    for expired in expired_assignments:
        # Mark previous assignment as failed
        expired.is_assigned = False
        expired.assigned_time = None
        expired.save()

        # Get the next employee in queue
        assign_order_to_next_employee()