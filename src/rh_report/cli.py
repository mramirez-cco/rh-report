"""
CLI principal para rh-report
"""

import os
import click
from .api_client import CatalogAPIClient
from .data_enrichment import enrich_dataframe
from .utils import load_dataframe, load_mapping_config, save_dataframe


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', 'output_file', default=None, 
              help='Archivo de salida (opcional)')
@click.option('--output-format', type=click.Choice(['csv', 'excel', 'json']), 
              default='csv',
              help='Formato del archivo de salida (default: csv)')
@click.option('--print', 'print_output', is_flag=True,
              help='Imprimir resultado a stdout en lugar de guardar en archivo (solo para csv/json)')
@click.option('--workers', '-w', default=10, 
              help='Número de workers concurrentes')
@click.option('--format', '-f', type=click.Choice(['csv', 'excel', 'json']), 
              default=None,
              help='Formato del archivo de entrada (auto-detectado si no se especifica)')
@click.option('--mapping', '-m', type=click.Path(exists=True),
              default=None,
              help='Archivo JSON con mapeo de columnas')
@click.version_option(version='1.0.0', prog_name='rh-report')
def main(input_file, output_file, output_format, print_output, workers, format, mapping):
    """
    Consulta información de repositorios e imágenes del Red Hat Catalog.

    INPUT_FILE: Archivo CSV, Excel o JSON con columnas 'name' e 'io.openshift.build.image'

    \b
    Ejemplos:
      rh-report reporte.xlsx
      rh-report --workers 20 reporte.csv
      rh-report --output-format json datos.json
      rh-report --output-format json --print datos.json
      rh-report --format csv --mapping config/mapping.json reporte.csv -o resultado.csv
      rh-report --output-format excel -o reporte.xlsx datos.csv
    """
    click.echo(click.style("🚀 Red Hat Catalog Image Reporter v1.0.0", fg='blue', bold=True))
    click.echo("")

    click.echo(f"📂 Cargando archivo: {click.style(input_file, fg='cyan')}")
    
    # Validar opciones de salida
    if print_output and output_format == 'excel':
        click.echo(click.style("No puedes usar --print con formato Excel", fg='red'), err=True)
        raise click.Abort()
    
    # Cargar mapeo de columnas si se proporciona
    column_mapping = None
    if mapping:
        try:
            click.echo(f"🔗 Cargando mapeo de columnas: {click.style(mapping, fg='cyan')}")
            column_mapping = load_mapping_config(mapping)
            click.echo(click.style("Mapeo cargado correctamente", fg='green'))
        except Exception as e:
            click.echo(click.style(f"Error cargando mapeo: {e}", fg='red'), err=True)
            raise click.Abort()

    try:
        df = load_dataframe(input_file, format_type=format, column_mapping=column_mapping)
    except Exception as e:
        click.echo(click.style(f"Error cargando archivo: {e}", fg='red'), err=True)
        raise click.Abort()

    click.echo(f"Registros encontrados: {click.style(str(len(df)), fg='green', bold=True)}")
    click.echo(f"Workers concurrentes: {click.style(str(workers), fg='yellow')}")
    click.echo("")

    click.echo(click.style("Consultando API de Red Hat Catalog...", fg='blue'))
    click.echo("")

    client = CatalogAPIClient(max_workers=workers)

    # Obtener nombres únicos
    unique_repositories = df["name"].unique().tolist()
    unique_images = df["io.openshift.build.image"].unique().tolist()

    click.echo(f"Repositorios únicos: {click.style(str(len(unique_repositories)), fg='cyan')}")
    click.echo(f"Imágenes únicas: {click.style(str(len(unique_images)), fg='cyan')}")
    click.echo("")

    # Consultar repositorios e imágenes concurrentemente
    try:
        results = client.fetch_repositories(unique_repositories)
        current_image_results = client.fetch_images(unique_images)
    except Exception as e:
        click.echo(click.style(f"Error consultando API: {e}", fg='red'), err=True)
        raise click.Abort()

    # Enriquecer DataFrame
    click.echo(click.style("Enriqueciendo datos...", fg='blue'))

    try:
        df = enrich_dataframe(df, results, current_image_results)
    except Exception as e:
        click.echo(click.style(f"Error enriqueciendo datos: {e}", fg='red'), err=True)
        raise click.Abort()

    # Guardar o imprimir resultado
    click.echo("")
    click.echo(click.style("Procesando salida...", fg='blue'))

    try:
        result = save_dataframe(
            df, 
            output_file=output_file,
            output_format=output_format,
            print_output=print_output
        )

        if result['mode'] == 'stdout':
            click.echo(result['data'])
        else:
            click.echo(click.style("Reporte generado exitosamente!", fg='green', bold=True))
            click.echo(f"Archivo: {click.style(result['output_file'], fg='cyan')}")
            click.echo(f"Formato: {click.style(result['format'].upper(), fg='yellow')}")
            click.echo(f"Total de registros: {click.style(str(len(df)), fg='yellow')}")
    except Exception as e:
        click.echo(click.style(f"Error guardando resultado: {e}", fg='red'), err=True)
        raise click.Abort()

    click.echo("")
    click.echo(click.style("Proceso completado", fg='magenta', bold=True))


if __name__ == '__main__':
    main()
