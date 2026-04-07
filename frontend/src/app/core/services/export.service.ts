import { Injectable } from '@angular/core';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

@Injectable({
    providedIn: 'root'
})
export class ExportService {

    constructor() { }

    /**
     * Exporta un arreglo de objetos JSON a un archivo Excel (.xlsx).
     * * @param {any[]} data - El arreglo de objetos con los datos a exportar.
     * @param {string} filename - El nombre que tendrá el archivo descargado (sin la extensión).
     * @param {string} [sheetName='Datos'] - El nombre de la pestaña dentro del Excel.
     * @returns {void}
     */
    exportToExcel(data: any[], filename: string, sheetName: string = 'Datos'): void {
        const worksheet: XLSX.WorkSheet = XLSX.utils.json_to_sheet(data);
        
        const workbook: XLSX.WorkBook = { 
            Sheets: { [sheetName]: worksheet }, 
            SheetNames: [sheetName] 
        };
        
        XLSX.writeFile(workbook, `${filename}.xlsx`);
    }

    /**
     * Exporta datos tabulares a un archivo PDF estructurado y estilizado.
     * * @param {string[]} headers - Arreglo con los títulos de las columnas.
     * @param {any[][]} data - Arreglo bidimensional (matriz) con los valores de las filas.
     * @param {string} filename - El nombre que tendrá el archivo descargado (sin la extensión).
     * @param {string} title - El título principal que aparecerá dentro del documento PDF.
     * @returns {void}
     */
    exportToPdf(headers: string[], data: any[][], filename: string, title: string): void {
        const doc = new jsPDF();

        doc.setFontSize(18);
        doc.setTextColor(31, 41, 55);
        doc.text(title, 14, 22);

        autoTable(doc, {
            head: [headers],
            body: data,
            startY: 30,
            theme: 'grid',
            styles: { 
                fontSize: 10, 
                cellPadding: 4,
                font: 'helvetica'
            },
            headStyles: { 
                fillColor: [99, 102, 241],
                textColor: [255, 255, 255],
                fontStyle: 'bold'
            },
            alternateRowStyles: {
                fillColor: [249, 250, 251]
            }
        });

        doc.save(`${filename}.pdf`);
    }
}