"""Compare chart contracts without pinning platform-sensitive t-SNE positions."""
import math


def compare(actual, expected):
    if type(expected) in (float, int):
        assert math.isclose(actual, expected, rel_tol=1e-5, abs_tol=1e-6), (actual, expected)
    elif isinstance(expected, list):
        assert len(actual) == len(expected)
        for left, right in zip(actual, expected):
            compare(left, right)
    elif isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key, value in expected.items():
            compare(actual[key], value)
    else:
        assert actual == expected, (actual, expected)


def tsne_contract(case):
    result = {key: value for key, value in case.items() if key != 'series'}
    result['series'] = []
    all_points = []
    for series in case['series']:
        points = series['points']
        assert points and all(len(point) == 2 and all(
            type(value) in (int, float) and math.isfinite(value) for value in point
        ) for point in points), 't-SNE must return finite 2D points'
        all_points.extend(points)
        result['series'].append({**series, 'points': len(points)})
    assert len(all_points) == 72, 'Keep every customer exactly once'
    for axis in (0, 1):
        values = [point[axis] for point in all_points]
        assert max(values) - min(values) > 1e-8, 't-SNE map collapsed'
    return result


def compare_ml_results(actual, expected, ident):
    if ident != '10':
        compare(actual, expected)
        return
    assert actual.keys() == expected.keys()
    assert len(actual['topics']) == len(expected['topics']) == 5
    # Existing experiments remain strict. Optimization may place t-SNE points
    # differently across BLAS/platform builds even with a fixed random_state.
    compare(actual['topics'][:4], expected['topics'][:4])
    compare([tsne_contract(case) for case in actual['topics'][4]],
            [tsne_contract(case) for case in expected['topics'][4]])
    for key in expected.keys() - {'topics'}:
        compare(actual[key], expected[key])


if __name__ == '__main__':
    import copy
    import json
    from pathlib import Path

    expected = json.loads((Path(__file__).resolve().parents[1] /
                           'ml/weeks/10/results.json').read_text(encoding='utf-8'))
    changed = copy.deepcopy(expected)
    for case in changed['topics'][4]:
        for series in case['series']:
            series['points'] = [[-2 * y + 10, 2 * x - 3] for x, y in series['points']]
    compare_ml_results(changed, expected, '10')
    mutations = [
        lambda data: data['topics'][0][0]['series'][0]['points'][0].__setitem__(0, 9999),
        lambda data: data['topics'][4][0]['series'][0]['points'].pop(),
        lambda data: data['topics'][4][0]['series'][0]['label'].__setitem__('ru', 'wrong group'),
        lambda data: data['topics'][4][0]['series'][0]['points'][0].__setitem__(0, float('nan')),
    ]
    for mutate in mutations:
        broken = copy.deepcopy(expected)
        mutate(broken)
        try:
            compare_ml_results(broken, expected, '10')
        except AssertionError:
            continue
        raise AssertionError('A broken chart must be rejected')
    print('PASS t-SNE platform-independent contracts; old charts, labels, row counts and finite coordinates stay checked')
