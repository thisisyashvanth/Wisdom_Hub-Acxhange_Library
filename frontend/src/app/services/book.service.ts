import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class BookService {

  // private baseUrl = 'http://localhost:8000/books';
  private baseUrl = `${environment.apiUrl}/books`


  constructor(private http: HttpClient) { }

  getAllBooks(): Observable<any> {
    return this.http.get(`${this.baseUrl}/get-all`);
  }

  // Pagination Version
  // getAllBooks(limit: number, lastKey?: any): Observable<any> {
  //   let params: any = { limit };

  //   if (lastKey) {
  //     params.last_key = JSON.stringify(lastKey);
  //   }

  //   return this.http.get(`${this.baseUrl}/get-all`, { params });
  // }

  addBook(req: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/add`, req);
  }

  getBookHistory(bookId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/${bookId}/users`);
  }

  // hrsignup(req: any) {
  //   return this.http.post(`${this.baseUrl}/hr-signup`, req);
  // }
}
