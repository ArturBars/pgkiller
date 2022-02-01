import asyncio

import asyncpg

from config import logger, apps, limit_connections


async def terminate(app, delay=60):
    credentials = apps[app]
    logger.info(f'Start listening app {app}.')
    while True:
        conn = await asyncpg.connect(**credentials)
        count = await conn.fetchval('''
                    select count(*)
                    from pg_stat_activity
                    where datname = $1
                      and pid <> pg_backend_pid();
                    ''', credentials['database'])
        if count > limit_connections:
            terminated = await conn.fetch('''
                            select pg_terminate_backend(pid)
                            from pg_stat_activity
                            where datname = $1
                                and pid <> pg_backend_pid();
                            ''', credentials['database'])
            logger.info(f'Killed {len(terminated)} connections in app {app}.')

        await asyncio.sleep(delay)


async def main():
    await asyncio.gather(*[terminate(app) for app in apps])


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
