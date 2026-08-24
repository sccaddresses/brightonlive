from brightonlive.pipeline import run
result=run("config/brighton.yaml",offline=True,fixtures=True)
print(result)
