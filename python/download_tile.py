from looker_sdk import client, models
import time
import sys

sdk = client.setup("../looker.ini")

def get_dashboard(title: str):
  """Get a dashboard by title"""
  dashboard = next(iter(sdk.search_dashboards(title=title)), None)
  if not dashboard:
    print(f"dashboard {title} was not found")
  return dashboard

def get_tile(dash: models.Dashboard, title: str):
  """Find a dashboard tile by title"""
  title = title.lower()
  found = None
  assert dash.dashboard_elements
  for tile in dash.dashboard_elements:
    assert tile.title
    if tile.title.lower() == title:
      break
  else:
    print(f"tile {title} of dashboard {dash.title} was not found")
    return None
  return tile

def download_tile(tile: models.DashboardElement, format:str = 'png'):
  """Download the dashboard tile in the specified format"""
  if not tile.query_id:
    print(f"tile {tile.title} has no query_id")
    return None
  task = sdk.create_query_render_task(
      query_id=tile.query_id, result_format=format, width=500, height=500)

  if (not task or not task.id):
    print(f"Could not create a render task for {tile.title}")
    return None

  # poll the render task until it completes
  elapsed = 0.0
  delay = 0.5 # wait .5 seconds
  while True:
    poll = sdk.render_task(task.id)
    if poll.status == 'failure':
      print(poll)
      print(f"Render failed for {tile.title}")
      return None
    elif poll.status == 'success':
      break

    time.sleep(delay)
    elapsed += delay
    print(f"{elapsed} seconds elapsed")

  result = sdk.render_task_results(task.id)
  fileName = f"{tile.title}.{format}"
  with open(fileName, 'wb') as f:
    f.write(result)
  return fileName

def main():
  dashboard_title = sys.argv[1] if len(sys.argv) > 1 else ""
  tile_title = sys.argv[2] if len(sys.argv) > 2 else ""
  render_format = sys.argv[3] if len(sys.argv) > 3 else "png"
  if not dashboard_title or not tile_title:
    print('Please provide: <dashboardTitle> <titleTitle> [<renderFormat>]')
    print('  renderFormat defaults to "png"')
    return

  dashboard = get_dashboard(dashboard_title)
  if dashboard:
    tile = get_tile(dashboard, tile_title)
    if (tile):
      download_tile(tile, render_format)

main()
