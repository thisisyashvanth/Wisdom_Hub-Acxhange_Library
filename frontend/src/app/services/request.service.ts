import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface RequestItem {
  request_id: string;
  employee_id: string;
  employee_name: string;
  book_id: string;
  book_name: string;
  request_type: string;
  status: string;
  requested_at: string;
  reviewed_at?: string;
  remarks?: string;
  is_restricted?: boolean;
}

export interface PaginatedRequests {
  data: RequestItem[];
  total: number;
  page: number;
  page_size: number;
}

@Injectable({
  providedIn: 'root'
})
export class RequestService {

  // private baseUrl = 'http://localhost:8000/request';
  private baseUrl = `${environment.apiUrl}/request`


  constructor(private http: HttpClient) { }

  borrow(book_id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/borrow/${book_id}`, {});
  }

  renew(borrowId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/renew/${borrowId}`, {});
  }

  returnBook(borrowId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/return/${borrowId}`, {});
  }

  reviewRequest(requestId: number, data: any): Observable<any> {
    return this.http.post(
      `${this.baseUrl}/${requestId}/review`,
      data
    );
  }

  getRequests(
    page: number,
    pageSize: number,
    statuses?: string[],
    search?: string
  ): Observable<PaginatedRequests> {

    let params = new HttpParams()
      .set('page', page)
      .set('page_size', pageSize);

    if (statuses) {
      statuses.forEach(s => {
        params = params.append('status', s);
      });
    }

    if (search) {
      params = params.set('search', search);
    }

    return this.http.get<PaginatedRequests>(`${this.baseUrl}/requests`, { params });
  }

  getMyRequests() {
    return this.http.get<any[]>(`${this.baseUrl}/my-requests`);
  }

  setUserRestriction(userId: string, restrict: boolean): Observable<any> {
    const params = new HttpParams().set('restrict', restrict);

    return this.http.post(
      `${this.baseUrl}/set-restriction/${userId}`,
      {},
      { params }
    );
  }
}