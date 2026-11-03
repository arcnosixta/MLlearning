"""Run official YOLO11n weights on a local image and save annotated detections."""

import argparse
from pathlib import Path


def probability(value):
    number = float(value)
    if not 0 <= number <= 1:
        raise argparse.ArgumentTypeError("value must be between 0 and 1")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="path to a local image you can use")
    parser.add_argument("--conf", type=probability, default=0.25)
    parser.add_argument("--iou", type=probability, default=0.45)
    parser.add_argument("--output", type=Path, default=Path("detected.jpg"))
    options = parser.parse_args()
    if not options.image.is_file():
        parser.error(f"image does not exist: {options.image}")
    if options.image.resolve() == options.output.resolve():
        parser.error("output must be different from the input")

    try:
        from ultralytics import YOLO
    except ModuleNotFoundError as error:
        raise SystemExit(f"Missing {error.name}. Install dependencies: python -m pip install ultralytics")
    model = YOLO("yolo11n.pt")
    result = model.predict(str(options.image), conf=options.conf, iou=options.iou,
                           device="cpu", verbose=False)[0]
    boxes = result.boxes.cpu()
    for category, score, coords in zip(boxes.cls.tolist(), boxes.conf.tolist(), boxes.xyxy.tolist()):
        print(f"{result.names[int(category)]}: confidence={score:.3f}, "
              f"xyxy={[round(pixel, 1) for pixel in coords]}")
    options.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(filename=str(options.output))
    print(f"{len(boxes)} detections saved to {options.output}")


if __name__ == "__main__":
    main()
