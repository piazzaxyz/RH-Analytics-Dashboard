from fastapi import APIRouter
from app.api.v1 import auth, employees, dashboard, timesheets, payroll, loans, evaluations, departments, alas, positions

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(employees.router)
router.include_router(departments.router)
router.include_router(alas.router)
router.include_router(positions.router)
router.include_router(dashboard.router)
router.include_router(timesheets.router)
router.include_router(payroll.router)
router.include_router(loans.router)
router.include_router(evaluations.router)
