import time

import conf
from engine import Engine

if __name__ == '__main__':
    e = Engine()
    e.login()

    submit_time = conf.submit_time
    while True:
        if True or time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) == submit_time:
            e.order_workflow(
                from_city=conf.from_city,
                to_city=conf.to_city,
                date=conf.date,
                train_id=conf.train_id,
                passengers=conf.passengers
            )
            break
        time.sleep(0.1)
