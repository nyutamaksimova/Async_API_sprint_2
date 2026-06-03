import asyncio

from redis.asyncio import Redis


async def wait_for_redis():
    redis_client = Redis(
        host='redis',
        port=6379,
    )

    while True:
        try:
            if await redis_client.ping():
                print('redis success')
                break
        except Exception:
            print('redis ping')

        await asyncio.sleep(1)

    await redis_client.aclose()


if __name__ == '__main__':
    asyncio.run(wait_for_redis())