import java.math.BigDecimal;
public class Main {
    public static void main(String[] args) {
        System.out.println(7 / 2);
        System.out.println(7 / 2.0);
        System.out.println(50000L * 50000);
        BigDecimal price = new BigDecimal("19.90");
        System.out.println(price.multiply(BigDecimal.valueOf(3)));
    }
}
