public class Main {
    static abstract class Shape {
        abstract int area();
        String label() { return "area=" + area(); }
    }
    static class Square extends Shape {
        private final int side;
        Square(int side) { this.side = side; }
        @Override int area() { return side * side; }
    }
    public static void main(String[] args) {
        Shape shape = new Square(4);
        System.out.println(shape.label());
    }
}
