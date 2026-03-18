#!/usr/bin/env python3
"""Seed alas e cargos por ala."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.ala import Ala
from app.models.position import Position

import app.models.ala
import app.models.position


ALAS_E_CARGOS = [
    ("DEV", "Desenvolvedores", [
        ("Estagiário DEV", "Estagiário de Desenvolvimento", 2000, "Estagiário"),
        ("Desenvolvedor Júnior Nível 1", "Desenvolvedor Júnior", 4000, "Júnior 1"),
        ("Desenvolvedor Júnior Nível 2", "Desenvolvedor Júnior", 5000, "Júnior 2"),
        ("Desenvolvedor Júnior Nível 3", "Desenvolvedor Júnior", 6000, "Júnior 3"),
        ("Desenvolvedor Pleno", "Desenvolvedor Pleno", 8000, "Pleno"),
        ("Desenvolvedor Sênior", "Desenvolvedor Sênior", 12000, "Sênior"),
    ]),
    ("DS", "Data Science", [
        ("Estagiário DS", "Estagiário de Data Science", 2000, "Estagiário"),
        ("Cientista de Dados Júnior", "Cientista de Dados Júnior", 5000, "Júnior"),
        ("Cientista de Dados Pleno", "Cientista de Dados Pleno", 9000, "Pleno"),
        ("Cientista de Dados Sênior", "Cientista de Dados Sênior", 14000, "Sênior"),
    ]),
    ("RH", "Recursos Humanos", [
        ("Estagiário RH", "Estagiário de RH", 1800, "Estagiário"),
        ("Analista RH Júnior", "Analista de RH Júnior", 3500, "Júnior"),
        ("Analista RH Pleno", "Analista de RH Pleno", 5000, "Pleno"),
        ("Analista RH Sênior", "Analista de RH Sênior", 7000, "Sênior"),
    ]),
    ("Marketing", "Marketing", [
        ("Estagiário Marketing", "Estagiário de Marketing", 1800, "Estagiário"),
        ("Analista de Marketing Júnior", "Analista de Marketing Júnior", 3500, "Júnior"),
        ("Analista de Marketing Pleno", "Analista de Marketing Pleno", 5500, "Pleno"),
        ("Analista de Marketing Sênior", "Analista de Marketing Sênior", 8000, "Sênior"),
    ]),
    ("Comercial", "Comercial", [
        ("Estagiário Comercial", "Estagiário Comercial", 1800, "Estagiário"),
        ("Analista Comercial Júnior", "Analista Comercial Júnior", 3500, "Júnior"),
        ("Analista Comercial Pleno", "Analista Comercial Pleno", 5500, "Pleno"),
        ("Analista Comercial Sênior", "Analista Comercial Sênior", 8000, "Sênior"),
    ]),
    ("Juridico", "Jurídico", [
        ("Estagiário Jurídico", "Estagiário Jurídico", 2000, "Estagiário"),
        ("Assessor Jurídico Júnior", "Assessor Jurídico Júnior", 5000, "Júnior"),
        ("Assessor Jurídico Pleno", "Assessor Jurídico Pleno", 7500, "Pleno"),
        ("Assessor Jurídico Sênior", "Assessor Jurídico Sênior", 11000, "Sênior"),
    ]),
    ("CTO", "CTO / Liderança Técnica", [
        ("Tech Lead", "Tech Lead", 15000, "Liderança"),
        ("CTO", "Chief Technology Officer", 25000, "C-Level"),
    ]),
    ("PO", "Product Owner", [
        ("Estagiário PO", "Estagiário de Produto", 2000, "Estagiário"),
        ("Product Owner Júnior", "Product Owner Júnior", 6000, "Júnior"),
        ("Product Owner Pleno", "Product Owner Pleno", 9000, "Pleno"),
        ("Product Owner Sênior", "Product Owner Sênior", 13000, "Sênior"),
    ]),
    ("Designer", "Design", [
        ("Estagiário Designer", "Estagiário de Design", 1800, "Estagiário"),
        ("Designer Júnior", "Designer Júnior", 3500, "Júnior"),
        ("Designer Pleno", "Designer Pleno", 5500, "Pleno"),
        ("Designer Sênior", "Designer Sênior", 8000, "Sênior"),
    ]),
]


def run_seed_alas():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Ala).count() > 0:
            print("Alas já existem. Pulando seed.")
            return

        for code, name, cargos in ALAS_E_CARGOS:
            ala = Ala(code=code, name=name)
            db.add(ala)
            db.flush()
            for title, desc, salary, level in cargos:
                pos = Position(
                    title=title,
                    description=desc,
                    base_salary=salary,
                    level=level,
                    ala_id=ala.id,
                )
                db.add(pos)
        db.commit()
        print(f"Seed alas: {db.query(Ala).count()} alas, {db.query(Position).count()} cargos criados.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed_alas()
