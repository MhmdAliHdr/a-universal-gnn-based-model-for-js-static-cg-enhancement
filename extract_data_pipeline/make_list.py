from multiprocessing import Process, Pipe

def f(conn):
    conn.send("HEY")
if __name__ == "__main__":
    v = 75
    conn1, conn2 = Pipe()
    p = Process(target=f, args=(conn2, ))
    p.start()
    p.join(300)
    v = conn1.recv()
    print(v)