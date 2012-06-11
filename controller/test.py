import time, random

def test_control(settings):
    yield "reset", ()
    while True:
        choice = random.randint(0, 2)
        distance = str(random.choice((-1, 1)) * random.uniform(0.9, 2.1))
        if choice == 0:
            yield "go", (distance, "0", "0")
        elif choice == 1:
            yield "go", ("0", distance, "0")
        elif choice == 2:
            yield "go", ("0", "0", distance)
        time.sleep(random.uniform(1.5, 4.4))
        yield "go", ("0", "0", "0")
        time.sleep(2.0)

