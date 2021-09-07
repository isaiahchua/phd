for %%g in (*.inp) do (
abaqus job=%%g int ask=off
)