# Tutorial: Run your first HIES validation

This tutorial takes a new contributor from a clean checkout to a successful validation of the shared contracts. It does not deploy a product.

## Prerequisites

- Git
- Python 3.12
- pip

## 1. Clone the repository

~~~bash
git clone https://github.com/LloydCoder/hezqen-infrastructure-standard.git
cd hezqen-infrastructure-standard
~~~

## 2. Create an isolated Python environment

~~~bash
python3 -m venv .venv
. .venv/bin/activate
~~~

On Windows PowerShell, activate with .venv\Scripts\Activate.ps1.

## 3. Install pinned validation dependencies

~~~bash
python -m pip install --only-binary=:all: -r requirements-dev.txt
~~~

## 4. Run the shared checks

~~~bash
python -m unittest discover -s tests -v
python scripts/validate-schemas.py
python scripts/validate-workflows.py
python scripts/validate-monorepo.py
python scripts/check-repo-hygiene.py .
~~~

A successful run means the checked-in tests and validators passed in your environment. It does not prove that a product works on hardware or infrastructure you did not test, and it is not a certification.

## 5. Explore a product

Start with the [product registry](../../products/README.md), then read the selected product README, threat model, compatibility notes, and operations guide before deploying it.
