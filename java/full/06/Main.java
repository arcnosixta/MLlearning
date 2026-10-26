public class Main {
    static final class Wallet {
        private long balance;
        Wallet(long balance) {
            if (balance < 0) throw new IllegalArgumentException("negative balance");
            this.balance = balance;
        }
        boolean withdraw(long amount) {
            if (amount <= 0) throw new IllegalArgumentException("positive amount required");
            if (amount > balance) return false;
            balance -= amount;
            return true;
        }
        long balance() { return balance; }
    }
    public static void main(String[] args) {
        Wallet wallet = new Wallet(100);
        System.out.println(wallet.withdraw(30));
        System.out.println(wallet.withdraw(90));
        System.out.println(wallet.balance());
    }
}
