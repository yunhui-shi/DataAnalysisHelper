def fibonacci(n):
    """生成斐波那契数列前n项
    
    参数:
        n (int): 要生成的斐波那契数列项数
        
    返回:
        list: 包含前n项斐波那契数列的列表
        
    示例:
        >>> fibonacci(5)
        [0, 1, 1, 2, 3]
    """
    if not isinstance(n, int):
        raise TypeError("输入必须是整数")
    if n < 0:
        raise ValueError("输入必须是非负整数")
    if n == 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])
    return sequence

if __name__ == "__main__":
    # 示例用法
    print("斐波那契数列前10项:", fibonacci(10))
    print("斐波那契数列前5项:", fibonacci(5))
