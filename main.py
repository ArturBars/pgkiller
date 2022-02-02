import asyncio

import asyncpg

from config import logger, APPS, LIMIT_CONNECTIONS, DELAY, CONNECTION_ATTEMPTS


async def terminate(app, delay=DELAY):
    credentials = APPS[app]

    conn = None
    attempts = CONNECTION_ATTEMPTS

    while conn is None and attempts > 0:
        logger.info(f'Trying to connect {app} db. '
                    f'Attempt {CONNECTION_ATTEMPTS - attempts + 1}.')
        try:
            conn = await asyncpg.connect(**credentials)
        except:
            attempts -= 1
            if not attempts:
                logger.info(f'Cannot connect to {app} db.')
                return
            await asyncio.sleep(5)
            continue

        logger.info(f'Connected to {app} db.')

        while True:
            try:
                count = await conn.fetchval('''
                            select count(*)
                            from pg_stat_activity
                            where datname = $1
                              and pid <> pg_backend_pid();
                            ''', credentials['database'])
                if count > LIMIT_CONNECTIONS:
                    terminated = await conn.fetch('''
                                    select pg_terminate_backend(pid)
                                    from pg_stat_activity
                                    where datname = $1
                                        and pid <> pg_backend_pid();
                                    ''', credentials['database'])
                    logger.info(
                        f'Killed {len(terminated)} connections in app {app}.')
            except Exception as exc:
                conn = None
                attempts = CONNECTION_ATTEMPTS
                logger.info(f'Lost connection with {app} db. '
                            f'Reason: {exc.args}')
                break

            await asyncio.sleep(delay)


async def main():
    await asyncio.gather(*[terminate(app) for app in APPS])


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
