from django.db.models import TextChoices

years = [
    ("OR", "Orientation"),
    ("FR", "Freshman"),
    ("SP", "Sophomore"),
    ("JN", "Junior"),
    ("SN", "Senior"),
]


class DepartmentEnum(TextChoices):

    ACFN = ("ACFN", "Accounting & Finance")
    AE = ("AE", "Aerospace Engineering")
    ARE = ("ARE", "Architectural Engineering")
    ARC = ("ARC", "Architecture")
    BIOE = ("BIOE", "Bioengineering")
    CE = ("CE", "Civil & Environmental Engg")
    CEM = ("CEM", "Construction Engg & Management")
    CHE = ("CHE", "Chemical Engineering")
    CHEM = ("CHEM", "Chemistry")
    CIE = ("CIE", "Control & Instrumentation Engineering")
    COE = ("COE", "Computer Engineering")
    CPG = ("CPG", "CPG")
    CRP = ("CRP", "City & Regional Planning")
    ERTH = ("ERTH", "Earth Sciences")
    EE = ("EE", "Electrical Engineering")
    ELI = ("ELI", "English Language Inst. (Prep)")
    ELD = ("ELD", "English Language Department")
    FIN = ("FIN", "Finance")
    ISOM = ("ISOM", "Info. Systems & Operations Mgt")
    GS = ("GS", "Global Studies")
    IAS = ("IAS", "Islamic & Arabic Studies")
    ICS = ("ICS", "Information & Computer Science")
    LS = ("LS", "Life Sciences")
    MATH = ("MATH", "Mathematics & Statistics")
    MBA = ("MBA", "Business Administration")
    ME = ("ME", "Mechanical Engineering")
    MSE = ("MSE", "Material Sciences and Engineering")
    MGT = ("MGT", "Management & Marketing")
    PE = ("PE", "Physical Education")
    PETE = ("PETE", "Petroleum Engineering")
    PHYS = ("PHYS", "Physics")
    PSE = ("PSE", "Prep Science & Engineering")
    # SE = ("SE", "Industrial and Systems Engineering")
    ISE = ("ISE", "Industrial and Systems Engineering")

    # not departments
    SWE = ("SWE", "Software Engineering")
    BUS = ("BUS", "Business")
