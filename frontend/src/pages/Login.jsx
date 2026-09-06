import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import Input from '../components/Input';
import Button from '../components/Button';
import { KeyRound } from 'lucide-react';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      toast.error('Please enter both username and password.');
      return;
    }

    setLoading(true);
    const result = await login(username, password);
    setLoading(false);

    if (result.success) {
      toast.success('Successfully logged in!');
      navigate('/dashboard');
    } else {
      toast.error(result.message);
    }
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      backgroundColor: '#f1f5f9'
    }}>
      <div className="card-enterprise" style={{
        width: '100%',
        maxWidth: '380px',
        padding: '30px 24px',
        backgroundColor: '#ffffff',
        border: '1px solid var(--border)',
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)'
      }}>
        <div style={{
          textAlign: 'center',
          marginBottom: '24px'
        }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '40px',
            height: '40px',
            backgroundColor: '#eff6ff',
            color: 'var(--primary)',
            borderRadius: '4px',
            marginBottom: '12px'
          }}>
            <KeyRound size={20} />
          </div>
          <h2 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '4px' }}>
            Sign in to Portal
          </h2>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Enterprise Procurement & Analytics
          </span>
        </div>

        <form onSubmit={handleSubmit}>
          <Input
            label="Username or Email"
            name="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="e.g. manager@enterprise.com"
            required
          />

          <Input
            label="Password"
            name="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />

          <Button
            type="submit"
            variant="primary"
            loading={loading}
            style={{ width: '100%', marginTop: '8px' }}
          >
            Sign In
          </Button>
        </form>

        <div style={{
          marginTop: '20px',
          paddingTop: '16px',
          borderTop: '1px solid var(--border)',
          textAlign: 'center',
          fontSize: '11px',
          color: 'var(--text-muted)'
        }}>
          <span>Default passwords are: <b>Password123</b></span>
        </div>
      </div>
    </div>
  );
};

export default Login;
