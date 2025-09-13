import typer
from typing import Optional
from repository import (
    create_person,
    list_people,
    get_person,
    update_person,
    delete_person,
    ensure_indexes,
    is_valid_email
)
from rich import print
from rich.table import Table
from rich.prompt import Prompt

app = typer.Typer(help="MongoCLI")

@app.callback()
def init():
    """
    Initialize indexes, ensure DB connectivity.
    """
    ensure_indexes()
    print("[green]Indexes ensured.[/green]")

@app.command("create")
def cmd_create(
    name: str = typer.Option(..., help="Name of the person"),
    email: str = typer.Option(..., help="Email address"),
    age: Optional[int] = typer.Option(None),
    address: Optional[str] = typer.Option(None)
):
    if not is_valid_email(email):
        print("[yellow]Warning: the email looks invalid[/yellow]")
    doc = {"name": name, "email": email}
    if age is not None:
        doc["age"] = age
    if address:
        doc["address"] = address
    inserted_id = create_person(doc)
    if inserted_id:
        print(f"[green]Created person with _id: {inserted_id}[/green]")
    else:
        print("[red]Failed to create person[/red]")

@app.command("list")
def cmd_list(
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search in name or email"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of records to list"),
    skip: int = typer.Option(0, "--skip", "-k", help="Number of records to skip")
):
    filter_q = {}
    if search:
        from bson.regex import Regex
        # or using a dict with $regex
        regex = {"$regex": search, "$options": "i"}
        filter_q = {"$or": [{"name": regex}, {"email": regex}]}
    people = list_people(filter_q=filter_q, limit=limit, skip=skip)
    if not people:
        print("[yellow]No records found.[/yellow]")
        raise typer.Exit()
    table = Table("ID", "Name", "Email", "Age", "Address")
    for p in people:
        table.add_row(
            str(p.get("_id")),
            p.get("name", ""),
            p.get("email", ""),
            str(p.get("age", "")),
            p.get("address", "") or ""
        )
    print(table)

@app.command("get")
def cmd_get(person_id: str = typer.Argument(..., help="ID of the person")):
    p = get_person(person_id)
    if not p:
        print("[red]Not found[/red]")
        raise typer.Exit(code=1)
    print(p)

@app.command("update")
def cmd_update(
    person_id: str = typer.Argument(..., help="ID of the person"),
    name: Optional[str] = typer.Option(None),
    email: Optional[str] = typer.Option(None),
    age: Optional[int] = typer.Option(None),
    address: Optional[str] = typer.Option(None)
):
    updates = {}
    if name:
        updates["name"] = name
    if email:
        if not is_valid_email(email):
            print("[yellow]Warning: email looks invalid[/yellow]")
        updates["email"] = email
    if age is not None:
        updates["age"] = age
    if address is not None:
        updates["address"] = address
    if not updates:
        print("[red]No updates specified[/red]")
        raise typer.Exit(code=1)
    ok = update_person(person_id, updates)
    if ok:
        print("[green]Update succeeded[/green]")
    else:
        print("[red]Update failed or nothing changed[/red]")

@app.command("delete")
def cmd_delete(person_id: str = typer.Argument(..., help="ID of the person")):
    confirm = typer.confirm(f"Are you sure you want to delete {person_id}?")
    if not confirm:
        print("[yellow]Delete cancelled[/yellow]")
        raise typer.Exit()
    ok = delete_person(person_id)
    if ok:
        print("[green]Deleted[/green]")
    else:
        print("[red]Delete failed or not found[/red]")

def register(app: typer.Typer):
    pass  # for possible modularity
