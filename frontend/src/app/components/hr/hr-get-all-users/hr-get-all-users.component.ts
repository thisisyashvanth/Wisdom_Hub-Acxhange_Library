import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { UserService } from '../../../services/user.service';
import { ExcelService } from '../../../services/excel.service';
import { RequestItem, RequestService } from '../../../services/request.service';

@Component({
  selector: 'app-hr-get-all-users',
  templateUrl: './hr-get-all-users.component.html',
  styleUrl: './hr-get-all-users.component.css'
})
export class HrGetAllUsersComponent {

  searchText: string = '';
  filteredUsers: any[] = [];

  users: any[] = [];
  loading: boolean = false;
  successMessage: string = '';
  errorMessage: string = '';

  pendingDeleteId: string | null = null;

  constructor(private router: Router, private userService: UserService, private excelService: ExcelService, private requestService: RequestService) { }

  ngOnInit(): void {
    this.getAllUsers();
  }

  getAllUsers() {
    this.loading = true;
    this.errorMessage = '';

    this.userService.getAllUsers().subscribe({
      next: (res: any) => {
        this.users = res;
        this.filteredUsers = res;
        this.loading = false;
        console.log(res);
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = 'Failed to load users';
        console.error(err);
      }
    });
  }

  filterUsers() {
    const term = this.searchText.toLowerCase();

    this.filteredUsers = this.users.filter(user =>
      (user.name?.toLowerCase().includes(term)) ||
      (user.employee_id?.toString().toLowerCase().includes(term))
    );
  }

  viewHistory(userId: number) {
    this.router.navigate(['/hr-user-view-history', userId]);
  }

  requestDelete(userId: string) {
    this.pendingDeleteId = userId;
    this.successMessage = '';
    this.errorMessage = '';
  }

  cancelDelete() {
    this.pendingDeleteId = null;
  }

  confirmDelete(userId: string) {
    this.userService.deleteUser(userId).subscribe({
      next: () => {
        this.users = this.users.filter(u => u.id !== userId);
        this.filteredUsers = this.filteredUsers.filter(u => u.id !== userId);
        this.pendingDeleteId = null;
        this.successMessage = 'User deleted successfully.';
        this.errorMessage = '';
      },
      error: (err) => {
        this.pendingDeleteId = null;
        this.errorMessage = err.error?.detail || 'Failed to delete user.';
        this.successMessage = '';
        console.error('Error deleting user:', err);
      }
    });
  }

  downloadExcel() {
    this.excelService.exportUsers(this.filteredUsers).subscribe({
      next: (blob: Blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');

        a.href = url;
        a.download = `users_${new Date().toISOString()}.xlsx`;

        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        this.errorMessage = 'Failed to download Excel';
        console.error(err);
      }
    });
  }

  onRestrictionChange(user: any, event: any) {
    const restrict = event.target.value === 'true';

    if (!user.id) {
      console.error('User ID missing:', user);
      this.errorMessage = 'Invalid user ID';
      return;
    }

    this.requestService.setUserRestriction(user.id, restrict).subscribe({
      next: () => {
        user.is_restricted = restrict;
        this.successMessage = 'Restriction updated successfully';
        this.errorMessage = '';
      },
      error: (err) => {
        console.error(err);
        this.errorMessage = 'Failed to update restriction';
        this.successMessage = '';
      }
    });
  }
}