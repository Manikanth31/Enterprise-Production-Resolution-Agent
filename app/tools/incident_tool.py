from app.tools.sql_tool import execute_readonly_sql


def investigate_incident(order_id: int):
    """Collect database evidence for an order-related incident."""

    evidence = {}

    evidence["order"] = execute_readonly_sql(
        f"""
        SELECT
            order_id,
            customer_id,
            order_status,
            order_amount
        FROM orders
        WHERE order_id = {order_id}
        """
    )

    evidence["invoice"] = execute_readonly_sql(
        f"""
        SELECT
            invoice_id,
            order_id,
            invoice_status,
            invoice_amount
        FROM invoices
        WHERE order_id = {order_id}
        """
    )

    evidence["payment"] = execute_readonly_sql(
        f"""
        SELECT
            payment_id,
            invoice_id,
            payment_status,
            payment_amount
        FROM payments
        WHERE invoice_id IN (
            SELECT invoice_id
            FROM invoices
            WHERE order_id = {order_id}
        )
        """
    )

    evidence["interface"] = execute_readonly_sql(
        f"""
        SELECT
            interface_id,
            interface_name,
            status,
            error_code,
            error_message
        FROM interface_transactions
        WHERE order_id = {order_id}
        """
    )

    evidence["errors"] = execute_readonly_sql(
        f"""
        SELECT
            e.error_id,
            e.error_code,
            e.error_message,
            e.severity
        FROM error_log e
        JOIN interface_transactions i
            ON e.interface_id = i.interface_id
        WHERE i.order_id = {order_id}
        """
    )

    return evidence