from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from apps.core.models import TimeStampedModel, SoftDeleteModel
from apps.company.models import Company


class JobTitle(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="job_titles"
    )
    title = models.CharField(max_length=255, verbose_name=_("Job Title"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    class Meta:
        db_table = "hris_job_titles"
        verbose_name = _("Job Title")
        verbose_name_plural = _("Job Titles")
        indexes = [
            models.Index(fields=["company", "title"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.company.name})"


class Location(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="locations"
    )
    name = models.CharField(max_length=255, verbose_name=_("Location Name"))
    address = models.TextField(blank=True, null=True, verbose_name=_("Address"))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("City"))
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Country"))

    class Meta:
        db_table = "hris_locations"
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        indexes = [
            models.Index(fields=["company", "name"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.company.name})"


class Department(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="departments"
    )
    name = models.CharField(max_length=255, verbose_name=_("Department Name"))
    parent_department = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_departments",
    )
    # Using string 'Employee' here to avoid circular dependencies
    manager = models.ForeignKey(
        "Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_departments",
    )

    class Meta:
        db_table = "hris_departments"
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        indexes = [
            models.Index(fields=["company", "name"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.company.name})"


class Position(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="positions"
    )
    job_title = models.ForeignKey(
        JobTitle, on_delete=models.PROTECT, related_name="positions"
    )
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="positions"
    )
    location = models.ForeignKey(
        Location, on_delete=models.PROTECT, related_name="positions"
    )
    reports_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="direct_reports",
        help_text=_("The position this role reports to."),
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "hris_positions"
        verbose_name = _("Position")
        verbose_name_plural = _("Positions")
        indexes = [
            models.Index(fields=["company", "department", "is_active"]),
            models.Index(fields=["company", "job_title"]),
        ]

    def __str__(self):
        return f"{self.job_title.title} - {self.department.name} ({self.company.name})"


class Employee(TimeStampedModel, SoftDeleteModel):
    class GenderChoice(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")

    class MaritalStatusChoice(models.TextChoices):
        SINGLE = "S", _("Single")
        MARRIED = "M", _("Married")
        DIVORCED = "D", _("Divorced")
        WIDOWED = "W", _("Widowed")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        blank=True,
        null=True,
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="employees"
    )
    employee_id = models.CharField(max_length=50, verbose_name=_("Employee ID"))
    
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_("Date of Birth"))
    gender = models.CharField(
        max_length=1, choices=GenderChoice.choices, blank=True, null=True
    )
    marital_status = models.CharField(
        max_length=1, choices=MaritalStatusChoice.choices, blank=True, null=True
    )
    contact_number = models.CharField(
        max_length=20, blank=True, null=True, verbose_name=_("Contact Number")
    )

    class Meta:
        db_table = "hris_employees"
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")
        unique_together = (("company", "employee_id"),)
        indexes = [
            models.Index(fields=["company", "employee_id"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"


class Employment(TimeStampedModel, SoftDeleteModel):
    class StatusChoice(models.TextChoices):
        ACTIVE = "active", _("Active")
        ON_LEAVE = "on_leave", _("On Leave")
        TERMINATED = "terminated", _("Terminated")
        RESIGNED = "resigned", _("Resigned")

    class TypeChoice(models.TextChoices):
        FULL_TIME = "full_time", _("Full-Time")
        PART_TIME = "part_time", _("Part-Time")
        CONTRACT = "contract", _("Contract")
        INTERN = "intern", _("Intern")

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="employments"
    )
    hire_date = models.DateField(verbose_name=_("Hire Date"))
    termination_date = models.DateField(blank=True, null=True, verbose_name=_("Termination Date"))
    status = models.CharField(max_length=20, choices=StatusChoice.choices, default=StatusChoice.ACTIVE)
    employment_type = models.CharField(max_length=20, choices=TypeChoice.choices, default=TypeChoice.FULL_TIME)

    class Meta:
        db_table = "hris_employments"
        verbose_name = _("Employment")
        verbose_name_plural = _("Employments")
        indexes = [
            models.Index(fields=["employee", "status"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.get_status_display()}"


class EmployeeAssignment(TimeStampedModel, SoftDeleteModel):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="assignments"
    )
    position = models.ForeignKey(
        Position, on_delete=models.PROTECT, related_name="assignments"
    )
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(blank=True, null=True, verbose_name=_("End Date"))
    is_primary = models.BooleanField(default=True, verbose_name=_("Is Primary Assignment"))

    class Meta:
        db_table = "hris_employee_assignments"
        verbose_name = _("Employee Assignment")
        verbose_name_plural = _("Employee Assignments")
        indexes = [
            models.Index(fields=["employee", "is_primary", "end_date"]),
            models.Index(fields=["position", "is_primary", "end_date"]),
        ]

    def __str__(self):
        return f"{self.employee} assigned to {self.position.job_title.title}"


class EmployeeDocument(TimeStampedModel, SoftDeleteModel):
    class DocumentTypeChoice(models.TextChoices):
        ID = "id", _("ID/Passport/Driver License")
        CONTRACT = "contract", _("Contract")
        CERTIFICATE = "certificate", _("Certificate/Degree")
        POLICY = "policy", _("Signed Policy")
        OTHER = "other", _("Other")

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="documents"
    )
    document_type = models.CharField(max_length=20, choices=DocumentTypeChoice.choices)
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    file = models.FileField(upload_to="hris/documents/%Y/%m/%d/", verbose_name=_("File"))

    class Meta:
        db_table = "hris_employee_documents"
        verbose_name = _("Employee Document")
        verbose_name_plural = _("Employee Documents")
        indexes = [
            models.Index(fields=["employee", "document_type"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.employee})"


class EmployeeEvent(TimeStampedModel, SoftDeleteModel):
    class EventTypeChoice(models.TextChoices):
        PROMOTION = "promotion", _("Promotion")
        DEMOTION = "demotion", _("Demotion")
        DISCIPLINARY = "disciplinary", _("Disciplinary Action")
        AWARD = "award", _("Award / Recognition")
        OTHER = "other", _("Other")

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="events"
    )
    event_type = models.CharField(max_length=20, choices=EventTypeChoice.choices)
    event_date = models.DateField(verbose_name=_("Event Date"))
    description = models.TextField(verbose_name=_("Description"))

    class Meta:
        db_table = "hris_employee_events"
        verbose_name = _("Employee Event")
        verbose_name_plural = _("Employee Events")
        indexes = [
            models.Index(fields=["employee", "event_type"]),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} for {self.employee} on {self.event_date}"


class AttendanceRecord(TimeStampedModel, SoftDeleteModel):
    class StatusChoice(models.TextChoices):
        PRESENT = "present", _("Present")
        ABSENT = "absent", _("Absent")
        HALF_DAY = "half_day", _("Half Day")
        LATE = "late", _("Late")

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="attendance_records"
    )
    date = models.DateField(verbose_name=_("Date"))
    check_in_time = models.TimeField(blank=True, null=True, verbose_name=_("Check In Time"))
    check_out_time = models.TimeField(blank=True, null=True, verbose_name=_("Check Out Time"))
    status = models.CharField(max_length=20, choices=StatusChoice.choices)

    class Meta:
        db_table = "hris_attendance_records"
        verbose_name = _("Attendance Record")
        verbose_name_plural = _("Attendance Records")
        unique_together = (("employee", "date"),)
        indexes = [
            models.Index(fields=["employee", "date"]),
            models.Index(fields=["employee", "status"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.get_status_display()})"


class LeaveRequest(TimeStampedModel, SoftDeleteModel):
    class LeaveTypeChoice(models.TextChoices):
        ANNUAL = "annual", _("Annual Leave")
        SICK = "sick", _("Sick Leave")
        MATERNITY = "maternity", _("Maternity Leave")
        PATERNITY = "paternity", _("Paternity Leave")
        UNPAID = "unpaid", _("Unpaid Leave")

    class StatusChoice(models.TextChoices):
        PENDING = "pending", _("Pending")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")
        CANCELLED = "cancelled", _("Cancelled")

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="leave_requests"
    )
    leave_type = models.CharField(max_length=20, choices=LeaveTypeChoice.choices)
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    status = models.CharField(max_length=20, choices=StatusChoice.choices, default=StatusChoice.PENDING)
    reason = models.TextField(verbose_name=_("Reason"))
    approved_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_leaves"
    )

    class Meta:
        db_table = "hris_leave_requests"
        verbose_name = _("Leave Request")
        verbose_name_plural = _("Leave Requests")
        indexes = [
            models.Index(fields=["employee", "status"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.get_leave_type_display()} ({self.get_status_display()})"
