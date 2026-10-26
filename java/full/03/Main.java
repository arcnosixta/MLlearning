public class Main {
    static int gcd(int a, int b) {
        if (a < 0 || b < 0) throw new IllegalArgumentException("nonnegative only");
        while (b != 0) {
            int remainder = a % b;
            a = b;
            b = remainder;
        }
        return a;
    }
    public static void main(String[] args) {
        System.out.println(gcd(48, 18));
        int sum = 0;
        for (int i = 1; i <= 5; i++) sum += i;
        System.out.println(sum);
        System.out.println(gcd(0, 0));
    }
}
