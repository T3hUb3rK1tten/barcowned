# If you run this on a private server, set this to "private"
# to enable file saving functionality
runMode = "public"

from os import listdir, path, getenv
import json
import os
from aiohttp import web
from aiohttp_index import IndexMiddleware

PROJECT_ROOT = path.dirname(path.abspath(__file__))
PAYLOADS_ROOT = path.join(PROJECT_ROOT, 'payloads')

async def handle_manifest(request):
	onlyfiles = [f for f in listdir(PAYLOADS_ROOT) if path.isfile(path.join(PAYLOADS_ROOT, f))]
	return web.Response(text=json.dumps(onlyfiles))

async def handle_rename(request):
  if runMode != "private":
    return web.Response(status=405) # method not allowed

  newPayloadName = await request.text()
  os.rename(path.join(PAYLOADS_ROOT, request.match_info['payload']), path.join(PAYLOADS_ROOT, newPayloadName))
  return web.Response(status=200)

async def handle_runmode(request):
	return web.Response(text=runMode)

async def handle_payload_put(request):
  if runMode != "private":
    return web.Response(status=405) # method not allowed
  payloadName = request.match_info['payload']
  payload = await request.text()
  with open(path.join(PAYLOADS_ROOT, payloadName), 'w+') as file:
    file.write(payload)
  return web.Response(status=204)

app = web.Application(middlewares=[IndexMiddleware()])

app.router.add_route('GET',
					path='/payloads/manifest.json',
					handler=handle_manifest)

app.router.add_route('PUT',
					path='/payloads/{payload}',
					handler=handle_payload_put)

app.router.add_route('PATCH',
          path='/rename-payload/{payload}',
          handler=handle_rename)

app.router.add_route('GET',
					path='/runmode',
					handler=handle_runmode)

app.router.add_static('/app',
					path=path.join(PROJECT_ROOT, 'app/build'),
					name='app',
					show_index=True)

app.router.add_static('/editor',
					path=path.join(PROJECT_ROOT, 'app/build'),
					name='app_editor',
					show_index=True)

app.router.add_static('/',
					path=PROJECT_ROOT,
					name='root',
					show_index=True)

web.run_app(app, port = int(getenv('PORT', 8080)))