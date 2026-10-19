/* Operator verification client, never register this general SQL runner as an AI tool.
 * java -cp /path/to/ojdbc11.jar RenewalSql.java statement.sql
 * Supply username, password and JDBC URL as three stdin lines from protected storage.
 * Credentials never appear in process arguments or output. One statement per file.
 */
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.sql.*;
import java.util.Properties;

class RenewalSql {
    public static void main(String[] args) throws Exception {
        if (args.length != 1) throw new IllegalArgumentException("Expected one SQL file");
        BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
        Properties props = new Properties();
        props.setProperty("user", input.readLine());
        props.setProperty("password", input.readLine());
        String url = input.readLine();
        props.setProperty("oracle.net.encryption_client", "REQUIRED");
        props.setProperty("oracle.net.encryption_types_client", "(AES256)");
        props.setProperty("oracle.net.crypto_checksum_client", "REQUIRED");
        // This EBS installation currently negotiates SHA1 integrity. Prefer SHA256
        // where enabled; require integrity and AES256 encryption in either case.
        props.setProperty("oracle.net.crypto_checksum_types_client", "(SHA256,SHA1)");
        props.setProperty("oracle.net.CONNECT_TIMEOUT", "10000");
        props.setProperty("oracle.jdbc.ReadTimeout", "60000");
        try (Connection conn = DriverManager.getConnection(url, props)) {
            conn.setAutoCommit(false);
            String sql = Files.readString(Path.of(args[0]));
            if (sql.stripLeading().startsWith("{?=")) {
                try (CallableStatement call = conn.prepareCall(sql)) {
                    call.registerOutParameter(1, Types.CLOB);
                    call.execute();
                    System.out.println(call.getString(1));
                    conn.commit();
                    return;
                }
            }
            try (Statement stmt = conn.createStatement()) {
                boolean rows = stmt.execute(sql);
                if (rows) {
                    try (ResultSet rs = stmt.getResultSet()) {
                        while (rs.next()) {
                            for (int col = 1; col <= rs.getMetaData().getColumnCount(); col++) {
                                if (col > 1) System.out.print(" | ");
                                System.out.print(rs.getString(col));
                            }
                            System.out.println();
                        }
                    }
                }
                conn.commit();
            } catch (SQLException ex) {
                conn.rollback();
                throw ex;
            }
        } catch (SQLException ex) {
            System.err.println(ex.getMessage().replace(url, "[connection]"));
            System.exit(1);
        }
    }
}
