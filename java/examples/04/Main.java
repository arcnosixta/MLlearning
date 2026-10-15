public class Main {
    static int sum(int[] values) {
        int result = 0;
        for (int value : values) result += value;
        return result;
    }
    public static void main(String[] args) {
        int[] marks = {10, 20, 30};
        System.out.println(sum(marks));
        System.out.println("Java".equals(new String("Java")));
    }
}
