uv add --dev notebook ipykernel
uv add matplotlib numpy pandas requests astroquery scipy
uv run python -m ipykernel install --user --name=nasa --display-name "Diagrama HR - Nasa Data"
echo Ambiente configurado com sucesso!
echo digite run
pause