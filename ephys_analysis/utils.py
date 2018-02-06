import numpy as np


def running_mean(x, N, mode='same'):
    """Efficient computation of running mean, that doesn't use convolve, which is slow

    Parameters
    ----------
    x: input signal
    N: length of window
    mode: {'same'}, 'valid'
        same: Pad that output signal so that it matches the shape of the input signal
        valid: Do not pad

    Returns
    -------

    """
    N = int(N)
    if N > len(x):
        raise ValueError('N cannot be greater than x')
    cumsum = np.cumsum(np.insert(x, 0, 0))
    mx = (cumsum[N:] - cumsum[:-N]) / float(N)
    if mode == 'valid':
        return mx
    elif mode == 'same':
        pad_before = np.ones(np.floor((N - 1) / 2).astype(np.int)) * mx[0]
        pad_after = np.ones(np.ceil((N - 1) / 2).astype(np.int)) * mx[-1]
        px = np.hstack((pad_before, mx, pad_after))
        return px


def rms(x, win_len):
    return np.sqrt(running_mean(x ** 2, win_len))


def isin_single_interval(tt, tbound, inclusive_left, inclusive_right):
    if inclusive_left:
        left_condition = (tt >= tbound[0])
    else:
        left_condition = (tt > tbound[0])

    if inclusive_right:
        right_condition = (tt <= tbound[1])
    else:
        right_condition = (tt < tbound[1])

    return left_condition & right_condition


def isin_time_windows(tt, tbounds, inclusive_left=True, inclusive_right=False):
    """Test whether input times are within a time window or a set of time windows

    Parameters
    ----------
    tt: np.array
        times, size = (n,)
    tbounds: np.array
        time windows, size = (k, 2)
    inclusive_left: bool
    inclusive_right: bool

    Returns
    -------
    logical indicating if time is in any of the windows, size = (n,)
    """

    # check if tbounds in np.array and if not fix it
    tbounds = np.array(tbounds)
    tt = np.array(tt)

    tf = np.zeros(tt.shape, dtype='bool')

    if len(tbounds.shape) is 1:
        tf = isin_single_interval(tt, tbounds, inclusive_left, inclusive_right)
    else:
        for tbound in tbounds:
            tf = tf | isin_single_interval(tt, tbound, inclusive_left, inclusive_right)
    return tf.astype(bool)


def threshcross(signal, thresh=0, direction='up'):
    """Finds the indices where a signal crosses a threshold.

    :param signal: np.array(Nx1)
    :param thresh: double, default=0
    :param direction: str, direction of crosses to detect. {'up'}, 'down', 'both'
    :return:
    """

    over = (signal >= thresh)
    cross = np.diff(over.astype('int'))

    if direction == 'up':
        return np.where(cross > 0)[0] + 1
    elif direction == 'down':
        return np.where(cross < 0)[0] + 1
    elif direction == 'both':
        up = np.where(cross > 0)[0] + 1
        down = np.where(cross < 0)[0] + 1
        if down[0] < up[0]:
            up = np.hstack([0, up])
        if up[-1] > down[-1]:
            down = np.hstack([down, len(signal)])
        return np.vstack([up, down]).T
