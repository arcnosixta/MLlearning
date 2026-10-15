public class Main {
    public static void main(String[] args) {
        int score = 75;
        if (score < 0 || score > 100) {
            System.out.println("invalid");
        } else if (score >= 90) {
            System.out.println("A");
        } else if (score >= 70) {
            System.out.println("B");
        } else {
            System.out.println("C");
        }
        String day = switch (2) { case 1 -> "Mon"; case 2 -> "Tue"; default -> "Other"; };
        System.out.println(day);
    }
}
