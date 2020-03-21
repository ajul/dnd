import numpy
import scipy.optimize

def dc_chance(dc):
    return (10.0 - abs(dc - 16.0)) / 100.0

def success_chance(bonus, lucky=False):
    result = 0.0
    for dc in range(7, 26):
        p_dc = dc_chance(dc)
        p_make = min(max(bonus + 21 - dc, 0), 20) / 20.0
        if lucky:
            p_make = 1.0 - (1.0 - p_make) ** 2.0
        result += p_dc * p_make
    return result

def result_chances(bonus, lucky=False):
    p_success = success_chance(bonus, lucky)
    return [
        (1.0 - p_success) ** 3.0,
        3.0 * (1.0 - p_success) ** 2.0 * p_success,
        3.0 * (1.0 - p_success) * p_success ** 2.0,
        p_success ** 3.0,
        ]

payoffs = [-2.0, -0.5, 0.5, 1.0]

def optimize_stake(bonus, lucky=False):
    p_results = result_chances(bonus, lucky)
    def objective(x):
        return sum(
            -numpy.log(1.0 + x * payoff) * p_result
            for p_result, payoff in zip(p_results, payoffs))

    result = scipy.optimize.minimize_scalar(objective, bounds=(0, 0.5), method='bounded')
    optimal_stake_percent = numpy.floor(result.x * 100.0)
    doubling_time = numpy.log(0.5) / objective(optimal_stake_percent / 100.0)
    return p_results, optimal_stake_percent, doubling_time

def generate_table(lucky=False):
    result = '<table>\n'
    result += '<tr><th rowspan="2">Bonus</th><th colspan="4">Successes</th>'
    result += '<th rowspan="2">Optimal stake</th><th rowspan="2">Mean doubling time (workweeks)</th></tr>\n'
    result += '<tr><th>0</th><th>1</th><th>2</th><th>3</th></tr>\n'
    for bonus in range(21):
        p_results, optimal_stake_percent, doubling_time = optimize_stake(bonus, lucky)
        result += '<tr><td>%+d</td><td>%0.1f%%</td><td>%0.1f%%</td><td>%0.1f%%</td><td>%0.1f%%</td>' % (
            bonus,
            p_results[0] * 100, p_results[1] * 100, p_results[2] * 100, p_results[3] * 100,
            )
        if doubling_time > 0.0:
            result += '<td>%d%%</td><td>%0.1f</td></tr>\n' % (optimal_stake_percent, doubling_time)
        else:
            result += '<td>-</td><td>-</td></tr>\n'
    result += '</table>\n'
    return result

print(generate_table(False))
