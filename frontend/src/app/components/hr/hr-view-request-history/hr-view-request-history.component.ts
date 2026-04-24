import { Component } from '@angular/core';
import { RequestService } from '../../../services/request.service';
import { ExcelService } from '../../../services/excel.service';

@Component({
  selector: 'app-hr-view-request-history',
  templateUrl: './hr-view-request-history.component.html',
  styleUrl: './hr-view-request-history.component.css'
})
export class HrViewRequestHistoryComponent {

  page = 1;
  pageSize = 10;
  total = 0;

  requests: any[] = [];
  filteredRequests: any[] = [];

  searchText: string = '';

  loading = false;
  successMessage = '';
  errorMessage = '';

  constructor(private requestService: RequestService, private excelService: ExcelService) { }

  ngOnInit(): void {
    this.loadRequests();
  }

  loadRequests() {
    this.loading = true;

    this.requestService.getRequests(
      this.page,
      this.pageSize,
      ['APPROVED', 'REJECTED'],
      this.searchText
    ).subscribe({
      next: (res) => {

        this.total = res.total;

        this.requests = res.data.map(r => ({
          id: r.request_id,
          book_title: r.book_name,
          user_name: r.employee_name,
          request_type: r.request_type,
          status: r.status,
          request_date: r.requested_at,
          return_date: r.reviewed_at,
          remarks: r.remarks
        }));

        this.filteredRequests = this.requests;
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to load requests';
        this.loading = false;
      }
    });
  }

  onSearch() {
    this.page = 1; 
    this.loadRequests();
  }

  downloadExcel() {
    this.excelService.exportRequests(this.filteredRequests).subscribe({
      next: (blob: Blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');

        a.href = url;
        a.download = `request_history_${new Date().toISOString()}.xlsx`;

        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        this.errorMessage = 'Failed to download Excel';
        console.error(err);
      }
    });
  }
}