from collections import deque


def search_pattern(lines, pattern, max_depth=5):
    dq = deque(maxlen=max_depth)
    for line in lines:
        if pattern in line:
            yield line, dq
        dq.append(line)


if __name__ == '__main__':
    with open('test.txt', 'r') as f:
        for line, dq in search_pattern(f, 'python', 3):
            print(line, dq)
