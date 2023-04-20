from invoke import task


@task
def pybabel_extract(c):
    c.run("pybabel extract -F babel.cfg -o messages.pot .")


@task
def pybabel_update(c):
    c.run("pybabel update -i messages.pot -d frontend/translations")


@task
def pybabel_compile(c):
    c.run("pybabel compile -d frontend/translations")
