'use strict';

const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/';
const SEABORN_WHEEL = 'https://files.pythonhosted.org/packages/83/11/00d3c3dfc25ad54e731d91449895a79e4bf2384dc3ac01809010ba88f6d5/seaborn-0.13.2-py3-none-any.whl';
const QUIET_DOWNLOAD = {messageCallback() {}, errorCallback() {}};
const MAX_CODE = 128_000;
const MAX_DATASET = 2_000_000;
const MAX_CAPTURE = 256_000;
const MAX_LOG = 120_000;

// Separate interpreter state for the runner and the student's __main__ module.
const RUN_SETUP = `
import os
import sys
import tempfile
from types import ModuleType

workdir = tempfile.TemporaryDirectory(prefix="imlearning-")
script_path = os.path.join(workdir.name, "lab.py")
previous_dir = os.getcwd()
previous_args = sys.argv
previous_path = sys.path.copy()
previous_main = sys.modules.get("__main__")
previous_streams = sys.stdout, sys.stderr
student = ModuleType("__main__")
student.__file__ = script_path
student_globals = student.__dict__

figures = []
shown = set()
pyplot = None
original_show = None
plot_style = None

def capture_figures(*args, **kwargs):
    from base64 import b64encode
    from io import BytesIO
    from math import isfinite

    for number in pyplot.get_fignums():
        if len(shown) >= 4:
            break
        figure = pyplot.figure(number)
        if figure in shown:
            continue
        shown.add(figure)
        width, height = figure.get_size_inches()
        if not all(isfinite(value) and value > 0 for value in (width, height)):
            continue
        with BytesIO() as png:
            figure.savefig(png, format="png", dpi=min(90, 960 / width, 720 / height))
            if png.tell() <= 420_000:
                figures.append(b64encode(png.getvalue()).decode("ascii"))

if has_matplotlib:
    import matplotlib.pyplot as pyplot
    pyplot.switch_backend("Agg")
    pyplot.close("all")
    plot_style = pyplot.rc_context()
    plot_style.__enter__()
    original_show = pyplot.show
    pyplot.show = capture_figures

os.chdir(workdir.name)
sys.path.insert(0, workdir.name)
sys.argv = [script_path]
sys.modules["__main__"] = student
`;

const RUN_CLEANUP = `
import linecache

sys.stdout, sys.stderr = previous_streams
sys.stdout.flush()
sys.stderr.flush()
if pyplot is not None and original_show is not None:
    pyplot.show = original_show
    pyplot.close("all")
    plot_style.__exit__(None, None, None)
sys.argv = previous_args
sys.path = previous_path
if previous_main is None:
    sys.modules.pop("__main__", None)
else:
    sys.modules["__main__"] = previous_main
for name, module in list(sys.modules.items()):
    path = getattr(module, "__file__", "")
    if isinstance(path, str) and path.startswith(workdir.name + "/"):
        sys.modules.pop(name, None)
linecache.cache.pop(script_path, None)
os.chdir(previous_dir)
workdir.cleanup()
`;

let runtimePromise;
let busy = false;

function runtime() {
  if (!runtimePromise) {
    runtimePromise = Promise.resolve().then(async () => {
      const {loadPyodide} = await import(PYODIDE_URL + 'pyodide.mjs');
      return loadPyodide({
        indexURL: PYODIDE_URL,
        // Course Python needs no browser objects or native file system handles.
        jsglobals: Object.create(null),
        env: {MPLBACKEND: 'Agg', OPENBLAS_NUM_THREADS: '1', OMP_NUM_THREADS: '1'},
      });
    }).catch(error => {
      runtimePromise = undefined;
      throw new Error(`Pyodide could not load from jsDelivr. ${error.message}`);
    });
  }
  return runtimePromise;
}

function createCapture() {
  const decoder = new TextDecoder();
  return {
    text: '',
    truncated: false,
    append(chunk) {
      const available = MAX_CAPTURE - this.text.length;
      this.text += chunk.slice(0, available);
      this.truncated ||= chunk.length > available;
    },
    write(bytes) {
      this.append(decoder.decode(bytes, {stream: true}));
      return bytes.length;
    },
    finish() {
      this.append(decoder.decode());
    },
  };
}

function localizedText(value) {
  return ['ru', 'kk'].every(lang =>
    typeof value?.[lang] === 'string' && value[lang].length > 0 && value[lang].length <= 2000);
}

function validExperiment(value) {
  return Array.isArray(value?.topics) && value.topics.length > 0 && value.topics.length <= 6
    && value.topics.every(cases => Array.isArray(cases) && cases.length > 0 && cases.length <= 6
      && cases.every(item => localizedText(item?.label) && localizedText(item?.note)
        && (item.xTicks === undefined || (Array.isArray(item.xTicks) && item.xTicks.length <= 32
          && item.xTicks.every(tick => Number.isFinite(tick?.value) && localizedText(tick?.label))))
        && Array.isArray(item.series) && item.series.length > 0 && item.series.length <= 16
        && item.series.every(series => localizedText(series?.label)
          && ['line', 'bar', 'scatter'].includes(series.kind)
          && Array.isArray(series.points) && series.points.length > 0 && series.points.length <= 1000
          && series.points.every(point => Array.isArray(point) && point.length === 2
            && point.every(Number.isFinite)))));
}

function readExperiment(capture) {
  if (capture.truncated) return null;
  const output = capture.text.trimEnd();
  const start = output.lastIndexOf('\n{') + 1;
  try {
    const experiment = JSON.parse(output.slice(start));
    return validExperiment(experiment) ? experiment : null;
  } catch {
    return null;
  }
}

function sendLog(id, stream, capture) {
  capture.finish();
  let text = capture.text.slice(0, MAX_LOG);
  if (capture.text.length > MAX_LOG || capture.truncated) text += '\n[…]\n';
  if (text) self.postMessage({type: 'output', id, stream, text});
}

async function loadPackages(pyodide, code) {
  await pyodide.loadPackagesFromImports(code, QUIET_DOWNLOAD);
  if (!code.includes('seaborn') || Object.hasOwn(pyodide.loadedPackages, 'seaborn')) return;
  const codeModule = pyodide.pyimport('pyodide.code');
  let imports;
  try {
    imports = codeModule.find_imports(code);
    if (imports.toJs().includes('seaborn')) {
      await pyodide.loadPackage(['numpy', 'pandas', 'scipy', 'matplotlib', SEABORN_WHEEL], QUIET_DOWNLOAD);
    }
  } finally {
    imports?.destroy();
    codeModule.destroy();
  }
}

async function run(id, code, dataset) {
  if (!runtimePromise) self.postMessage({type: 'status', id, phase: 'loading'});
  const pyodide = await runtime();
  self.postMessage({type: 'status', id, phase: 'packages'});
  await loadPackages(pyodide, code);

  const stdout = createCapture();
  const stderr = createCapture();
  const scope = pyodide.runPython('dict()');
  let studentGlobals;
  let figures;
  try {
    pyodide.setStdout({write: bytes => stdout.write(bytes)});
    pyodide.setStderr({write: bytes => stderr.write(bytes)});
    pyodide.setStdin({stdin: () => null});
    scope.set('has_matplotlib', Object.hasOwn(pyodide.loadedPackages, 'matplotlib'));
    pyodide.runPython(RUN_SETUP, {globals: scope});
    studentGlobals = scope.get('student_globals');
    const filename = scope.get('script_path');
    const directory = filename.slice(0, filename.lastIndexOf('/'));
    pyodide.FS.writeFile(filename, code, {encoding: 'utf8'});
    if (dataset) pyodide.FS.writeFile(`${directory}/data.csv`, dataset.text, {encoding: 'utf8'});
    self.postMessage({type: 'status', id, phase: 'running'});
    const result = await pyodide.runPythonAsync(code, {
      globals: studentGlobals,
      filename,
      dedent: false,
    });
    if (result instanceof pyodide.ffi.PyProxy) result.destroy();
    figures = JSON.parse(pyodide.runPython(`
if pyplot is not None:
    capture_figures()
import json
json.dumps(figures)
`, {globals: scope}));
  } finally {
    try {
      if (scope.has('previous_streams')) pyodide.runPython(RUN_CLEANUP, {globals: scope});
    } finally {
      studentGlobals?.destroy();
      scope.destroy();
      pyodide.setStdout({batched() {}});
      pyodide.setStderr({batched() {}});
      sendLog(id, 'stdout', stdout);
      sendLog(id, 'stderr', stderr);
    }
  }
  const experiment = readExperiment(stdout);
  self.postMessage({
    type: 'result',
    id,
    figures,
    ...(experiment && {experiment}),
  });
}

self.addEventListener('message', async ({data}) => {
  if (data?.type !== 'run' || !Number.isSafeInteger(data.id)) return;
  const {id, code, dataset} = data;
  const validDataset = dataset === undefined || (dataset?.name === 'data.csv'
    && typeof dataset.text === 'string' && dataset.text.length <= MAX_DATASET);
  if (busy || typeof code !== 'string' || code.length > MAX_CODE || !validDataset) {
    self.postMessage({type: 'error', id, message: busy ? 'A lab is already running.' : 'Invalid lab input.'});
    return;
  }
  busy = true;
  try {
    await run(id, code, dataset);
  } catch (error) {
    const message = String(error?.message || error);
    self.postMessage({type: 'error', id, message: message.slice(0, MAX_LOG)});
  } finally {
    busy = false;
  }
});
