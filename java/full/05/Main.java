public class Main {
    /** Returns the sum without modifying the arguments. */
    static long sum(int... values) {
        long result = 0;
        for (int value : values) result += value;
        return result;
    }
    public static void main(String[] args) {
        int[] grades = {2, 3, 5};
        System.out.println(sum(grades));
        System.out.println(sum());
        System.out.println(grades[0]);
    }
}
