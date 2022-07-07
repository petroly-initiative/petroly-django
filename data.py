from django.db.models import TextChoices

years = [
    ("OR", "Orientation"),
    ("FR", "Freshman"),
    ("SP", "Sophomore"),
    ("JN", "Junior"),
    ("SN", "Senior"),
]


class DepartmentEnum(TextChoices):

    AF = ("AF", "Accounting & Finance")
    AE = ("AE", "Aerospace Engineering")
    ARE = ("ARE", "Architectural Engineering")
    ARC = ("ARC", "Architecture")
    CE = ("CE", "Civil & Environmental Engg")
    CEM = ("CEM", "Construction Engg & Management")
    CHE = ("CHE", "Chemical Engineering")
    CHEM = ("CHEM", "Chemistry")
    COE = ("COE", "Computer Engineering")
    CPG = ("CPG", "CPG")
    CRP = ("CRP", "City & Regional Planning")
    ERTH = ("ERTH", "Earth Sciences")
    EE = ("EE", "Electrical Engineering")
    ELI = ("ELI", "English Language Inst. (Prep)")
    ELD = ("ELD", "English Language Department")
    FIN = ("FIN", "Finance")
    ISOM = ("ISOM", "Info. Systems & Operations Mgt")
    GS = ("GS", "Global & Social Studies")
    IAS = ("IAS", "Islamic & Arabic Studies")
    ICS = ("ICS", "Information & Computer Science")
    LS = ("LS", "Life Sciences")
    MATH = ("MATH", "Mathematics & Statistics")
    MBA = ("MBA", "Business Administration")
    ME = ("ME", "Mechanical Engineering")
    MGT = ("MGT", "Management & Marketing")
    PE = ("PE", "Physical Education")
    PETE = ("PETE", "Petroleum Engineering")
    PHYS = ("PHYS", "Physics")
    PSE = ("PSE", "Prep Science & Engineering")
    SE = ("SE", "Systems Engineering")
