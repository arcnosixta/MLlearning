public class Main {
    abstract static class Shape { abstract double area(); }
    static final class Square extends Shape {
        private final double side;
        Square(double side) {
            if (!Double.isFinite(side) || side < 0) throw new IllegalArgumentException();
            this.side = side;
        }
        @Override double area() { return side * side; }
    }
    public static void main(String[] args) {
        Shape[] shapes = {new Square(3), new Square(4)};
        double total = 0;
        for (Shape shape : shapes) total += shape.area();
        System.out.println(total);
    }
}
