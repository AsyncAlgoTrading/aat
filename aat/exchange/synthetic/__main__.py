import asyncio
import os
from . import main


if __name__ == '__main__':
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        asyncio.get_event_loop().run_until_complete(main(int(os.environ.get('PORT', '5000'))))
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print('terminating...')
