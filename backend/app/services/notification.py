"""
Módulo de servicios para el envío de notificaciones y alertas.
Integra el SDK de Brevo (anteriormente Sendinblue) para correos transaccionales.
"""
import logging
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from app.core.config import settings
from app.models.product import Product

logger = logging.getLogger(__name__)

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = settings.BREVO_API_KEY

class NotificationService:
    """
    Servicio encargado de gestionar las notificaciones salientes del sistema.
    """

    @staticmethod
    def send_low_stock_email(product: Product) -> bool:
        """
        Arma y envía un correo electrónico de alerta cuando un producto 
        cae por debajo de su stock mínimo.
        
        Args:
            product (Product): La instancia del producto con stock bajo.
            
        Returns:
            bool: True si el correo se envió con éxito, False en caso contrario.
        """
        if not settings.BREVO_API_KEY:
            logger.warning("BREVO_API_KEY no está configurada. Se omite el envío de correo.")
            return False

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        subject = f"⚠️ Alerta de Stock Crítico: {product.name} ({product.sku})"

        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Alerta de Inventario - StockFlow</title>
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0B0914; margin: 0; padding: 0; color: #F8F5FF;">
            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #0B0914; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #151123; border-radius: 12px; border: 1px solid #241B3B; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);">
                            
                            <tr>
                                <td align="center" style="padding: 30px 20px 20px 20px; border-bottom: 1px solid #241B3B;">
                                    <img src="https://approvingly-gemological-alonso.ngrok-free.dev/static/icono.png" alt="StockFlow Logo" width="48" height="48" style="display: block; margin-bottom: 10px; border-radius: 50%;">
                                    <h2 style="margin: 0; font-size: 20px; color: #F8F5FF; letter-spacing: 1px;">StockFlow</h2>
                                </td>
                            </tr>

                            <tr>
                                <td style="background-color: #EF4444; padding: 15px 20px; text-align: center;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 18px; font-weight: 600;">⚠️ Acción Requerida: Stock Crítico</h1>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="padding: 30px;">
                                    <p style="font-size: 16px; line-height: 1.6; margin-top: 0; color: #A594C6;">Hola Administrador,</p>
                                    <p style="font-size: 16px; line-height: 1.6; color: #F8F5FF;">El sistema de monitoreo ha detectado que un producto ha alcanzado o caído por debajo de su umbral de seguridad. Se recomienda iniciar el proceso de reposición.</p>
                                    
                                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #0B0914; border: 1px solid #241B3B; border-radius: 8px; margin: 25px 0;">
                                        <tr>
                                            <td style="padding: 20px;">
                                                <h3 style="margin-top: 0; margin-bottom: 15px; color: #8B5CF6; font-size: 16px; border-bottom: 1px solid #241B3B; padding-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;">Detalles del Producto</h3>
                                                <table width="100%" border="0" cellspacing="0" cellpadding="10" style="font-size: 15px;">
                                                    <tr>
                                                        <td width="35%" style="color: #A594C6; font-weight: 600;">Producto:</td>
                                                        <td width="65%" style="color: #F8F5FF;">{product.name}</td>
                                                    </tr>
                                                    <tr>
                                                        <td style="color: #A594C6; font-weight: 600;">Código SKU:</td>
                                                        <td style="color: #F8F5FF;">{product.sku}</td>
                                                    </tr>
                                                    <tr>
                                                        <td style="color: #A594C6; font-weight: 600;">Stock Actual:</td>
                                                        <td style="color: #EF4444; font-weight: bold; font-size: 16px;">{product.current_stock} {product.unit_of_measure}</td>
                                                    </tr>
                                                    <tr>
                                                        <td style="color: #A594C6; font-weight: 600;">Stock Mínimo:</td>
                                                        <td style="color: #F8F5FF;">{product.min_stock} {product.unit_of_measure}</td>
                                                    </tr>
                                                    <tr>
                                                        <td style="color: #A594C6; font-weight: 600;">Proveedor:</td>
                                                        <td style="color: #F8F5FF;">{product.supplier or 'No especificado'}</td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 0; color: #A594C6;">Por favor, contacte a su proveedor a la brevedad para evitar quiebres de stock que afecten las operaciones.</p>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="background-color: #0B0914; padding: 20px; text-align: center; border-top: 1px solid #241B3B;">
                                    <p style="margin: 0; font-size: 12px; color: #A594C6;">Este es un mensaje automático generado por el Sistema de Gestión StockFlow.</p>
                                    <p style="margin: 5px 0 0 0; font-size: 12px; color: #A594C6;">Por favor, no responda a este correo.</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        sender = {"name": settings.SENDER_NAME, "email": settings.SENDER_EMAIL}
        to = [{"email": settings.ALERT_EMAIL_DESTINATION}]
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            html_content=html_content,
            sender=sender,
            subject=subject
        )

        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Alerta enviada con éxito para el producto {product.sku}. Message ID: {api_response.message_id}")
            return True
        except ApiException as e:
            logger.error(f"Excepción al enviar correo vía Brevo: {e}")
            return False