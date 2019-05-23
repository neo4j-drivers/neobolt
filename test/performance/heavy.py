

import cProfile
import tracemalloc

from neobolt.direct import connect


def main():
    records = []
    with connect(("localhost", 7687), auth=("neo4j", "password")) as cx:
        for _ in range(10000):
            metadata = {}
            cx.run("RETURN 1", {}, on_success=metadata.update)
            cx.pull_all(on_records=records.extend, on_success=metadata.update)
            cx.send_all()
            cx.fetch_all()


def trace_allocation():
    tracemalloc.start()

    main()

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    for stat in top_stats:
        f = stat.traceback[0].filename
        if "neobolt" in f and ".virtualenvs" not in f:
            print(stat)


def profile():
    cProfile.run('main()', sort="cumtime")


if __name__ == "__main__":
    profile()
