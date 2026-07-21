import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ children, className = '', onClick }) => {
  return (
    <div onClick={onClick} className={`executive-card rounded-2xl p-6 relative overflow-hidden ${className}`}>
      {children}
    </div>
  );
};

export const CardHeader: React.FC<{ title: string; subtitle?: string; icon?: React.ReactNode; rightElement?: React.ReactNode }> = ({
  title,
  subtitle,
  icon,
  rightElement
}) => {
  return (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-3">
        {icon && (
          <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            {icon}
          </div>
        )}
        <div>
          <h3 className="text-lg font-bold text-slate-100 dark:text-slate-100 light:text-slate-900 tracking-tight">
            {title}
          </h3>
          {subtitle && (
            <p className="text-xs font-medium text-slate-400 dark:text-slate-400 light:text-slate-500 mt-0.5">
              {subtitle}
            </p>
          )}
        </div>
      </div>
      {rightElement && <div>{rightElement}</div>}
    </div>
  );
};
