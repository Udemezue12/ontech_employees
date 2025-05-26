from .models import CustomUser


def is_allowed_to_create_user(user):
    return user.role in [CustomUser.HR_MANAGER, CustomUser.MANAGER, CustomUser.OVERALL_ADMIN]


def is_allowed_to_create_salaries(user):
    return user.role in [CustomUser.HR_MANAGER, CustomUser.MANAGER, CustomUser.OVERALL_ADMIN]


def is_allowed_to_create_performance(user):
    return user.role in [CustomUser.HR_MANAGER, CustomUser.MANAGER, CustomUser.OVERALL_ADMIN]


def is_allowed_to_create_tax_deduction(user):
    return user.role in [CustomUser.MANAGER, CustomUser.OVERALL_ADMIN]


def is_allowed_to_create_leave_balance(user):
    return user.role in [CustomUser.MANAGER, CustomUser.OVERALL_ADMIN]


def check_can_assign_tasks(user):
    return user.is_authenticated and user.role in [CustomUser.HR_MANAGER, CustomUser.MANAGER, CustomUser.OVERALL_ADMIN]


def check_can_review_tasks(user):
    return user.is_authenticated and user.role in [CustomUser.HR_MANAGER, CustomUser.MANAGER, CustomUser.OVERALL_ADMIN]

def is_admin_or_manager(user):
    return user.role in ['Overall_Admin', 'Manager']